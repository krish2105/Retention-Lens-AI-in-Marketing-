# Restore drill

Run 2026-11-01T15:31:06+00:00 by `python3 scripts/restore_drill.py` against a SYNTHETIC database seeded through the API by scripts/seed_synthetic_state.py (5 workspaces; no uploads, because scoring needs the ML worker).

- Result: **PASSED**
- Backup `retentionlens-20261101T153106Z.sqlite3`, 774,144 bytes, checksum matches
- `PRAGMA integrity_check`: ok
- Restore and verification took 0.003 s
- Row counts matched the live database for all 14 tables

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

Recovery point: the last nightly backup (up to 24 h of decisions could be lost). Recovery time: the restore above plus restarting the API.
