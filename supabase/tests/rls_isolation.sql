-- Two-tenant isolation check for the Postgres policies. Run against a Supabase branch or local stack
-- (supabase start; psql "$DB_URL" -f supabase/tests/rls_isolation.sql). Raises an exception on any leak.
begin;
insert into auth.users (id, email) values ('00000000-0000-0000-0000-00000000000a', 'a@test'), ('00000000-0000-0000-0000-00000000000b', 'b@test');
insert into public.orgs (id, name) values ('org_a', 'A'), ('org_b', 'B');
insert into public.memberships values ('org_a', '00000000-0000-0000-0000-00000000000a', 'owner', now()), ('org_b', '00000000-0000-0000-0000-00000000000b', 'viewer', now());
insert into public.reviews (org_id, customer_id, decision, note, reviewer) values ('org_a', '1', 'contact', 'private to A', 'a');

set local role authenticated;
set local request.jwt.claims = '{"sub": "00000000-0000-0000-0000-00000000000b", "role": "authenticated"}';
do $$ begin
  if (select count(*) from public.reviews) <> 0 then raise exception 'LEAK: org B can read org A reviews'; end if;
  if (select count(*) from public.orgs where id = 'org_a') <> 0 then raise exception 'LEAK: org B can see org A'; end if;
  begin
    insert into public.reviews (org_id, customer_id, decision, note, reviewer) values ('org_b', '2', 'contact', 'viewer write', 'b');
    raise exception 'LEAK: a viewer could write';
  exception when insufficient_privilege or check_violation then null;
  end;
end $$;
rollback;
