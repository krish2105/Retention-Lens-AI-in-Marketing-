# SaaS production security and governance gates

## This ZIP is not production-hardened
Starter API uses **unauthenticated demo routes**, broad development CORS and local SQLite. Those choices are suitable ONLY for localhost demonstration and cannot protect customer data.

## Phase gates
1. **Before permissioned data:** customer-specific data agreement, least privilege, minimised fields, secrets outside source control, TLS, encrypted storage and approved retention.
2. **Before multi-tenant pilots:** authentication, role-based permissions, row-level tenant isolation tested across all API endpoints and async jobs; signed URLs for storage; audit log; access review.
3. **Before payment:** billing-provider integration, product entitlements, usage metering, invoices/tax jurisdiction review, refunds, abuse limits and business continuity plan.
4. **Before general release:** backup/restore drill, incident runbook, SAST/dependency scans, privacy/security review, structured monitoring and performance load tests.

## LLM / agent boundaries
- Retrieval only from permitted tenant documents, always with reliable source pointers.
- Prompt-injection defence: treat uploaded content as data, not authority; tool-use permissions server enforced.
- No irreversible action without explicit confirmation; idempotency tokens for side-effecting operations.
- If retrieval is empty/conflicted or confidence low, abstain and route for review.
- Output logs must redact sensitive information; no client PII in shared evaluation corpora.

## Reliability
- Input schemas, prepared SQL, request-size limits, rate limits, per-task timeouts and transaction-safe data changes.
- Durable jobs with clear retry semantics and dead-letter handling; ensure multiple retries do not duplicate actions.
- Saved draft recovery after network disruption; degraded-mode messaging with no silent data loss.
- Versioned export contracts, DB migrations, rollbacks and post-deployment smoke checks.
