# Restore drill (Postgres)

Run 2026-11-01T19:31:03+00:00 by `scripts/restore_drill_postgres.py` against a local Postgres 17 database seeded with SYNTHETIC workspaces by scripts/seed_synthetic_state.py.

- Result: **PASSED**
- `pg_dump -Fc` of schema `seeded`: 51,704 bytes; restored into a fresh database with `pg_restore`, then dropped
- Dump, restore and verification took 0.76 s
- Row counts matched for every table

| Table | Rows |
|---|---|
| audit_events | 1,095 |
| billing_events | 0 |
| critic_labels | 50 |
| datasets | 0 |
| drafts | 50 |
| idempotency | 25 |
| invites | 10 |
| memberships | 5 |
| orgs | 6 |
| outreach_outcomes | 160 |
| reviews | 1,000 |
| sessions | 5 |
| users | 5 |
| waitlist | 40 |
