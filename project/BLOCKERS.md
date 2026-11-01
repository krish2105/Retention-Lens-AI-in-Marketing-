# Open blockers and risk ownership (updated 2026-11-01 after the R1–R8 build)

| Blocker | Impact | Owner / mitigation |
|---|---|---|
| Assessment dates, solo permission, Cloud Lab, "deep learning" wording unconfirmed | Scope and marking risk | Owner: send the coordinator email; record rulings in DECISIONS.md |
| No interviews, usability sessions or pilot | CEO/CMO/MVP/SaaS lenses capped; commercial claims untested | Owner: `docs/research/INTERVIEW_KIT.md`, `docs/pilot/PILOT_KIT.md` |
| Labs and exercises log (60% of marks) not written | Largest marks risk | Owner: `docs/COURSEWORK_REVIEW.md` lists what to write |
| Nothing hosted; Supabase RLS not applied; no Stripe test keys | SaaS lens capped; real customer data must not be loaded | Owner creates accounts; then `render.yaml`, `supabase/README.md` |
| AI critic uncalibrated (0 of 16 human labels); 1 of 16 live drafts pass all checks | GenAI quality unproven | Owner labels drafts; then iterate prompt/model |
| Value ranges too narrow before Christmas (74.2% peak coverage) | Under-states uncertainty in peak season | Next model task: calibrate by season or widen peak-window residuals |
| 20 hours a week across five courses | Schedule | Prioritise graded writing over new features |

Resolved since the starter: git repository and CI, dataset checksum and data card, outcomes B and D built,
auth and tenant isolation (app-level, tested), backups with a restore drill.
