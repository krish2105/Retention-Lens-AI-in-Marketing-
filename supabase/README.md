# Supabase (prepared, not yet applied)

`migrations/0001_tenancy.sql` is the Postgres version of the API's tenancy model, with row-level
security on every tenant table and per-org folders in a private Storage bucket.
`tests/rls_isolation.sql` proves that a member of org B cannot read org A and that viewers cannot write.

Status: **not applied.** It needs a Supabase project owned by the project owner. Steps:

1. Create a project at supabase.com (free tier), then `supabase link --project-ref <ref>`.
2. `supabase db push` to apply the migration.
3. Run the isolation test on a branch database: `psql "$DB_URL" -f supabase/tests/rls_isolation.sql`.
4. Put the JWT secret in the API's environment as `SUPABASE_JWT_SECRET` and set `RL_AUTH_MODE=supabase`.

Until then the API's SQLite tenancy (same org_id rule, enforced in every query and tested in
`services/api/tests/test_tenancy.py`) is what runs.
