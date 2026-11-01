-- RetentionLens multi-tenant schema for Supabase Postgres, with row-level security (R3).
-- Mirrors services/api/app/db.py. Apply with: supabase db push  (needs the owner's Supabase project).
-- Rule: every tenant table has org_id, and a user can only touch rows of orgs they belong to.

create table if not exists public.orgs (
  id text primary key default 'o_' || substr(md5(random()::text), 1, 16),
  name text not null,
  plan text not null default 'pilot' check (plan in ('pilot', 'starter', 'growth')),
  use_sample boolean not null default false,
  active_dataset text,
  stripe_customer text,
  created_at timestamptz not null default now()
);

create table if not exists public.memberships (
  org_id text not null references public.orgs (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  role text not null check (role in ('owner', 'reviewer', 'viewer')),
  created_at timestamptz not null default now(),
  primary key (org_id, user_id)
);

-- Helper functions run as the definer so policies can check membership without recursion.
create or replace function public.is_member(target_org text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.memberships where org_id = target_org and user_id = auth.uid());
$$;

create or replace function public.has_role(target_org text, minimum text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.memberships
    where org_id = target_org and user_id = auth.uid()
      and (case role when 'owner' then 2 when 'reviewer' then 1 else 0 end)
          >= (case minimum when 'owner' then 2 when 'reviewer' then 1 else 0 end)
  );
$$;

create table if not exists public.datasets (
  id text primary key,
  org_id text not null references public.orgs (id) on delete cascade,
  filename text not null,
  sha256 text not null,
  bytes bigint not null,
  status text not null,
  stage text,
  pct int not null default 0,
  attempts int not null default 0,
  mapping jsonb,
  date_order text not null default 'auto',
  inspect jsonb,
  validation jsonb,
  summary jsonb,
  error text,
  created_by text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (org_id, sha256)
);

create table if not exists public.reviews (
  id bigserial primary key,
  org_id text not null references public.orgs (id) on delete cascade,
  customer_id text not null,
  decision text not null check (decision in ('contact', 'keep_watching', 'no_action')),
  note text not null,
  reviewer text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.drafts (
  id bigserial primary key,
  org_id text not null references public.orgs (id) on delete cascade,
  customer_id text not null,
  status text not null,
  source text not null,
  model text,
  subject text not null,
  body text not null,
  checks jsonb not null,
  context jsonb not null,
  recipient_type text,
  consent_basis text,
  decided_by text,
  decided_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.outreach_outcomes (
  id bigserial primary key,
  org_id text not null references public.orgs (id) on delete cascade,
  customer_id text not null,
  week date not null,
  arm text not null check (arm in ('contact', 'holdout')),
  contacted_at timestamptz,
  reordered_at date,
  checked_through date,
  created_at timestamptz not null default now(),
  unique (org_id, customer_id, week)
);

create table if not exists public.critic_labels (
  org_id text not null references public.orgs (id) on delete cascade,
  draft_id bigint not null references public.drafts (id) on delete cascade,
  label text not null check (label in ('pass', 'revise')),
  note text not null default '',
  labeller text not null,
  created_at timestamptz not null default now(),
  primary key (org_id, draft_id)
);

-- Append-only: no update or delete policy is granted to users.
create table if not exists public.audit_events (
  id bigserial primary key,
  org_id text not null,
  at timestamptz not null default now(),
  actor text not null,
  action text not null,
  subject text not null,
  detail jsonb not null
);

create index if not exists reviews_org on public.reviews (org_id, customer_id);
create index if not exists drafts_org on public.drafts (org_id, status);
create index if not exists audit_org on public.audit_events (org_id, id);

alter table public.orgs enable row level security;
alter table public.memberships enable row level security;
alter table public.datasets enable row level security;
alter table public.reviews enable row level security;
alter table public.drafts enable row level security;
alter table public.outreach_outcomes enable row level security;
alter table public.critic_labels enable row level security;
alter table public.audit_events enable row level security;

create policy orgs_read on public.orgs for select using (public.is_member(id));
create policy orgs_owner_update on public.orgs for update using (public.has_role(id, 'owner'));
create policy orgs_owner_delete on public.orgs for delete using (public.has_role(id, 'owner'));

create policy memberships_read on public.memberships for select using (public.is_member(org_id));
create policy memberships_owner_write on public.memberships for all using (public.has_role(org_id, 'owner')) with check (public.has_role(org_id, 'owner'));

-- Read for any member; write for reviewers and owners.
do $$
declare t text;
begin
  foreach t in array array['datasets', 'reviews', 'drafts', 'outreach_outcomes', 'critic_labels'] loop
    execute format('create policy %1$s_read on public.%1$s for select using (public.is_member(org_id))', t);
    execute format('create policy %1$s_insert on public.%1$s for insert with check (public.has_role(org_id, ''reviewer''))', t);
    execute format('create policy %1$s_update on public.%1$s for update using (public.has_role(org_id, ''reviewer'')) with check (public.has_role(org_id, ''reviewer''))', t);
    execute format('create policy %1$s_delete on public.%1$s for delete using (public.has_role(org_id, ''owner''))', t);
  end loop;
end $$;

create policy audit_read on public.audit_events for select using (public.is_member(org_id));
create policy audit_insert on public.audit_events for insert with check (public.is_member(org_id));

-- Uploaded files: one Storage bucket, one folder per org (path "<org_id>/<file>").
insert into storage.buckets (id, name, public) values ('uploads', 'uploads', false) on conflict (id) do nothing;
create policy uploads_read on storage.objects for select using (bucket_id = 'uploads' and public.is_member((storage.foldername(name))[1]));
create policy uploads_write on storage.objects for insert with check (bucket_id = 'uploads' and public.has_role((storage.foldername(name))[1], 'reviewer'));
create policy uploads_delete on storage.objects for delete using (bucket_id = 'uploads' and public.has_role((storage.foldername(name))[1], 'owner'));
