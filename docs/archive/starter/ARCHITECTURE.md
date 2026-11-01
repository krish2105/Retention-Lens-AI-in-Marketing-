# End-to-end technical architecture — RetentionLens

```mermaid
flowchart TD
  U["User / organisation"] --> W["Next.js dashboard, light/dark/system"]
  W --> A["FastAPI authenticated API - future"]
  A --> Q["Validation + idempotent import"]
  Q --> P[("PostgreSQL tenant data - future")]
  Q --> F[("Object storage + provenance - future")]
  P --> T["Versioned offline features and training"]
  T --> M["Model registry + calibration"]
  M --> I["Prediction service with abstain/fallback"]
  P --> I
  I --> R["Domain rules / checks / constraints"]
  R --> W
  W --> H["Human review + audit + outcomes"]
  H --> P
  F --> G["Permission-aware citations / RAG, when justified"]
  G --> W
```

## Starter state (implemented)
- Frontend: Next.js React client pages, theme mode, interactive queue/review view, responsive CSS; fetches local API.
- Backend: FastAPI `/api/health`, `/api/demo/records`, `/api/demo/summary`, `/api/demo/domain`, `/api/demo/import`, `/api/demo/reviews`; SQLite seeded from synthetic sample.
- `services/api/app/domain.py` is a tested deterministic domain calculation, NOT an ML predictor.
- `data/sample/demo_cases.csv` contains fictional domain records. Import is a **demo-only JSON CSV text endpoint**; it is not hardened for arbitrary untrusted files.

## Production target (planned, not implemented)
- Identity: external OAuth/email auth, organisations, roles, sessions, rotation, revocation.
- Tenant isolation: PostgreSQL row-level policies plus application authorization and tests across orgs.
- Ingestion: async job queue, strict schemas, source version, idempotency, backpressure, quarantine, signed checksums.
- Source storage: immutable object versions, encryption, retention, deletion and consent.
- Training: reproducible scripts or orchestrated jobs, tracking seeds/hardware/data checksums, model lineage and approval.
- Serving: clear response schema `{prediction, uncertainty, evidence, version, status, limitations}` with conservative fallback and monitoring.
- RAG: scoped retrieval; chunk provenance; evaluation of faithfulness and retrieval quality; no unverified free-text math.
- Review engine: durable state machine (draft / queued / reviewed / approved / rejected), audit/event outbox and idempotent external actions.
- Operations: structured logs excluding sensitive data, traces, alerts, backup restore test, billing events and per-tenant quotas.

## Why this architecture
Start monolithic to minimize solo-builder coordination cost. Extract services only when load, isolation or lifecycle warrants it. No vector database or agent framework until the workflow has actual relevant approved documents.

## Database entities (proposed)
`organization`, `user`, `membership`, `data_source`, `data_import`, `source_record`, `model_run`, `model_version`, `prediction`, `evidence_link`, `review_case`, `review_action`, `audit_event`, `subscription`, `usage_event`. Every customer row has tenant_id, provenance, created_at and version semantics. Sensitive fields must be minimized.
