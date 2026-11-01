# Load test

2026-11-01T19:30:35+00:00 · 20 concurrent simulated reviewers for 30 s against one local API process (uvicorn, 1 worker, Postgres 17 (local, pooled), reference dataset of 5,852 accounts) on a MacBook, with the per-IP rate limit raised because every simulated user shares one address. `scripts/load_test.py`.

- 12,620 requests, 420.7 per second, 0 errors
- All reads p50 42.0 ms, p95 85.6 ms
- SLO (no errors, every read route p95 under 500 ms): **met**

| Route | Requests | Errors | p50 ms | p95 ms | p99 ms |
|---|---|---|---|---|---|
| account detail | 1,826 | 0 | 59.4 | 95.4 | 150.3 |
| account search | 1,857 | 0 | 39.3 | 72.2 | 139.3 |
| accounts page | 1,839 | 0 | 40.4 | 70.3 | 140.2 |
| cohorts | 1,743 | 0 | 36.4 | 70.3 | 128.8 |
| queue | 1,800 | 0 | 59.2 | 96.1 | 161.6 |
| segments | 1,758 | 0 | 36.3 | 67.0 | 140.2 |
| summary | 1,797 | 0 | 36.1 | 69.6 | 145.5 |

Limits: one machine, warm caches, no network latency, no sign-in. A hosted test should be repeated after deployment.
