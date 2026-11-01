# Restore drill

Run 2026-11-01T14:11:21+00:00 by `python3 scripts/restore_drill.py` against the local API database.

- Result: **PASSED**
- Backup `retentionlens-20261101T141121Z.sqlite3`, 151,552 bytes, checksum matches
- `PRAGMA integrity_check`: ok
- Restore and verification took 0.002 s
- Row counts matched the live database for all 14 tables

| Table | Rows |
|---|---|
| audit_events | 5 |
| billing_events | 0 |
| critic_labels | 0 |
| datasets | 0 |
| drafts | 1 |
| idempotency | 0 |
| invites | 0 |
| memberships | 0 |
| orgs | 1 |
| outreach_outcomes | 64 |
| reviews | 0 |
| sessions | 0 |
| users | 0 |
| waitlist | 0 |

Recovery point: the last nightly backup (up to 24 h of decisions could be lost). Recovery time: the restore above plus restarting the API.
