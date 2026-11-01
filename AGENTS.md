# Agent operating contract — RetentionLens

## Authority and recovery order
1. Read `course/outline.docx` (assessment requirements), `docs/ASSESSMENT.md` and `README.md`.
2. Read `project/CURRENT_STATE.md`, `project/DECISIONS.md`, `project/BLOCKERS.md`, `project/NEXT_ACTIONS.md`, and last 20 entries of `project/SESSION_LOG.md`.
3. Inspect actual code, tests, git status and dependencies; **documents can be stale**. Verify claims by execution.
4. Do not infer work from previous chat context. If a file or test is absent, label it absent.

## Working method
- One independent MAIB AI 208 project. Keep its coursework, generated code, datasets and reports separate from other subjects.
- Solo owner, 20 hours/week shared among FIVE projects; no unapproved mega-refactors or scope creep.
- Produce a short task plan and write acceptance criteria before edits. Implement one vertical slice at a time.
- Distinguish: VERIFIED OBSERVATION, SYNTHETIC DEMO, ASSUMPTION, HYPOTHESIS, TODO. Do not silently fill missing customer fields with defaults.
- Confirm data licensing and access; do not scrape around access controls, fabricate participant data, or copy prohibited documents.
- Save reproducible evidence: raw-data checksum/URL/version, configuration, seeds, train/val/test definitions, models, metrics, stderr, screenshots.
- For UI, implement light/dark/system mode, WCAG contrast, keyboard states, error/empty/loading/success states, mobile layouts and chart data provenance.
- For external effects (emails, purchase orders, approvals, grading, financial recommendations) require explicit permission, verified idempotency and a human approval gate.

## Exit protocol (mandatory EVERY session)
Update `project/CURRENT_STATE.md` with completed/verified items, commands run, observed outputs, currently changed files, unresolved blockers and next runnable task. Append a dated entry to `project/SESSION_LOG.md`. Update decisions and backlog. State what remains untested.

## Initial first action
Run the synthetic demo and unit tests, audit course outcome mapping, then implement the highest-priority **unverified** milestone from `project/NEXT_ACTIONS.md`. Do not claim it is production-ready.
