# Load test

2026-11-01T14:13:56+00:00 · 20 concurrent simulated reviewers for 30 s against one local API process (uvicorn, 1 worker, SQLite, reference dataset of 5,852 accounts) on a MacBook, with the per-IP rate limit raised because every simulated user shares one address. `scripts/load_test.py`.

- 10,261 requests, 342.0 per second, 0 errors
- All reads p50 25.5 ms, p95 270.9 ms
- SLO (no errors, every read route p95 under 500 ms): **met**

| Route | Requests | Errors | p50 ms | p95 ms | p99 ms |
|---|---|---|---|---|---|
| account detail | 1,483 | 0 | 32.8 | 54.8 | 92.2 |
| account search | 1,494 | 0 | 24.2 | 46.9 | 82.1 |
| accounts page | 1,513 | 0 | 24.9 | 48.2 | 107.5 |
| cohorts | 1,431 | 0 | 21.4 | 40.9 | 118.7 |
| queue | 1,464 | 0 | 257.6 | 311.8 | 328.4 |
| segments | 1,423 | 0 | 20.8 | 41.7 | 82.6 |
| summary | 1,453 | 0 | 21.1 | 39.9 | 91.6 |

Limits: one machine, warm caches, no network latency, no sign-in. A hosted test should be repeated after deployment.
