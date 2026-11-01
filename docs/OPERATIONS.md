# Operations runbook (R4)

## Service level objectives

| Objective | Target | Latest evidence |
|---|---|---|
| Read API latency | p95 under 500 ms per read route, no errors | `reports/load_test.md` (20 users, 30 s: met) |
| Scoring job | 100k invoice lines in under 5 minutes | 114,886 synthetic lines scored in 9.1 s (MacBook, 2026-11-01) |
| Availability | 99.5% monthly (hosted) | Not measured yet: no hosted deployment |
| Recovery point / time | 24 h / under 1 h | `reports/restore_drill.md` (passed) |

**Load-test history.** The first run (2026-11-01) found the weekly queue at p95 1,045 ms: it wrote to SQLite on
every read, so readers waited for the write lock. Fixed by writing assignments only on first sight; re-run p95 312 ms.
An earlier run hit the API's own per-IP rate limit (429s), which is why the load test raises `RL_RATE_LIMIT_PER_MIN`.

## Observability

- Every request logs one JSON line: time, request ID, method, route template, status, milliseconds. No bodies.
- `GET /api/metrics`: p50/p95 per route and 5xx counts since start, with the SLO targets.
- `GET /api/status` (public): database, reference data, scoring worker, jobs by status, local AI. Shown at `/status`.
- `X-Request-ID` is returned on every response; quote it when reporting a problem.

## Backups and restore

- Nightly: `python3 scripts/backup_db.py` (online SQLite backup + SHA-256, keeps 14).
- Monthly drill: `cd scripts && python3 restore_drill.py` → `reports/restore_drill.md`. A failed drill is an incident.
- Uploaded files live under `RL_DATA_DIR`; back up that folder with the host's disk snapshots.
- On Supabase: use point-in-time recovery and still run a restore drill into a branch database.

## Incidents

1. Note the time, the symptom and a request ID. Check `/status` and the logs.
2. If customer data may be exposed: stop the service, then follow the DPA breach clause (tell the customer within 48 h).
3. Fix, then write up using the template below in `docs/incidents/YYYY-MM-DD-title.md`.

```
# Incident: <title>
- Detected: <time, how>          - Resolved: <time>
- Impact: <who, what, how long>  - Data exposed: yes / no (evidence)
- Timeline:
- Root cause:
- What we changed:
- What we will change:
```

## Common tasks

| Task | Command |
|---|---|
| Run the API with sign-in | `RL_AUTH_MODE=local services/api/.venv/bin/uvicorn app.main:app --app-dir services/api --port 8001` |
| Rebuild reference scores | `cd ml && uv run python -m retentionlens.cli serve && python3 ../scripts/export_static_data.py` |
| Re-run R5 experiment | `cd ml && uv run python -m retentionlens.cli r5` |
| Load test | `services/api/.venv/bin/python scripts/load_test.py --base http://localhost:8001` |
| Browser tests (static) | `cd apps/web && npx playwright test` |
| Browser tests (full app) | API on 8001 + `npm run dev`, then `npm run test:e2e:live` |
| Waitlist count | `curl -H "X-Admin-Token: $RL_ADMIN_TOKEN" $API/api/admin/waitlist` |
