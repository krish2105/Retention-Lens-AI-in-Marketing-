# Security checklist: OWASP ASVS 4.0 Level 1 (selected requirements)

Self-assessed by the build, 2026-11-01. "Met" means implemented **and** covered by a test or a check in CI.
Sign-off by a second person is still needed (R3 gate).

| Area | Requirement (ASVS) | Status | Evidence |
|---|---|---|---|
| Passwords | 2.1.1 at least 12 characters | Met | `SignUp` model; `test_signup_signin_signout_and_password_rules` |
| Passwords | 2.4.1 stored with an approved slow hash | Met | scrypt N=2^14 in `app/security.py` |
| Passwords | 2.2.1 anti-automation on sign-in | Met | 10 attempts/min per IP; `test_signin_is_rate_limited` |
| Passwords | 2.1.7 breached/common-password check | Partly | Offline deny-list, low-variety and email-in-password checks (tested); online k-anonymity lookup when hosted |
| Sessions | 3.2.1 new token at sign-in, 3.2.2 ≥128 bits | Met | `secrets.token_urlsafe(32)`, only the SHA-256 stored |
| Sessions | 3.3.1 sign-out invalidates the session | Met | Session row deleted; test checks 401 after sign-out |
| Sessions | 3.4.1–3.4.3 cookie Secure, HttpOnly, SameSite | Met | `RL_COOKIE_SECURE=1` when hosted |
| Access control | 4.1.1 enforced on the server | Met | `ctx`/`require` on every route; every query filters `org_id` |
| Access control | 4.1.3 least privilege | Met | owner / reviewer / viewer; viewer write → 403 (tested) |
| Access control | 4.2.1 no direct object reference across tenants | Met | `test_two_tenant_isolation` (drafts, datasets, audit by id) |
| Access control | 4.2.2 CSRF protection | Met | JSON bodies and a custom header force a CORS pre-flight; origins allow-listed |
| Validation | 5.1.3 input validated on the server | Met | Pydantic models with lengths and enums; upload type and size limits |
| Output | 5.3.x encoding; CSV/formula injection | Met | React escaping; CSV cells starting `= + - @` neutralised (tested) |
| LLM output | (OWASP LLM05) model output treated as untrusted | Met | Deterministic checks block links, markup, contact data, leaks |
| Files | 12.1.1 size limit, 12.1.2 type allow-list | Met | 50 MB, .csv/.xlsx only; stored outside the web root, never executed |
| Files | 12.3.1 user file names not used as paths | Met | Stored as `<dataset_id><ext>` |
| Secrets | 2.10.4 / 14.x no secrets in the repo | Met | `.env` ignored; `.env.example` has blanks; live Stripe keys refused |
| Config | 14.4.x security headers | Met | nosniff, frame DENY, no-referrer, CSP on API responses, HSTS when secure |
| Dependencies | 14.2.1 components up to date, scanned | Met | `pip-audit`, `npm audit --audit-level=high`, CodeQL in CI |
| Logging | 7.1.1 no credentials or bodies in logs | Met | Access log has route, status and timing only |
| Audit | 7.2.x security events logged | Met | Decisions, invites, roles, deletions and failed sign-ins (email hashed) logged; per-account sign-in throttle |
| Data | 8.3.x export and deletion | Met | `/api/org/export`, `/api/org/delete` (tested) |
| Comms | 9.1.1 TLS everywhere | Pending | Depends on hosting (Render/Azure provide TLS); not deployed yet |
| Rate limits | 11.1.4 anti-automation on costly actions | Met | Uploads 20/h per org, drafts 30/min per org, global per-IP limit |

Open items: online breached-password lookup, hosted TLS, external sign-off, and a
penetration test before real customer data.
