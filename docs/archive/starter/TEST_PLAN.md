# Quality gates and end-to-end acceptance

## Currently runnable (after local dependency install)
1. `PYTHONPATH=services/api pytest -q services/api/tests`.
2. Start FastAPI. `curl -s http://localhost:8000/api/health`.
3. `curl -s http://localhost:8000/api/demo/records` and `curl -s http://localhost:8000/api/demo/domain`.
4. Start Next.js, browse to http://localhost:3000, switch Light/Dark/System, search a synthetic case, submit a review note and observe persisted status after refresh.

## Tests Work must implement before claiming real MVP
- Correct results for known tiny input and edge cases (zero, missing, duplicates, malformed, out-of-range).
- Import end-to-end on a **genuinely permissible sample** with schema mismatch feedback and totals reconciliation.
- Model training/retraining reproducibility, leakage checks, baseline comparison, inference from held-out records and artifact signature.
- Real user flow: new tenant -> connect/import -> validated result -> human review -> export -> return -> audit.
- 2+ tenant isolation tests, role-based access, denied cross-tenant reads, job ownership tests.
- Failure injection: API unavailable, interrupted upload, retry, corrupt source, LLM unavailable, model missing.
- UI keyboard/mouse and reduced-motion audit; theme persistence and colour contrast.
- Billing/usage and restore test when commercially relevant.

## Release evidence table
| Claim | Required evidence | Current status |
|---|---|---|
| Runnable demo | API/unit test logs + screenshot after local run | Code provided; installation/run not yet performed by user |
| Real data processing | Import manifest, license, checksum, field validation | Not implemented |
| Trained model | Run configs, artifacts, held-out metrics | Not implemented |
| Academic superiority | Frozen-test comparison and uncertainty | Not established |
| SaaS readiness | Security tests and pilot logs | Not established |
