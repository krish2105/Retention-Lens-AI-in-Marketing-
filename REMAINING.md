# What is remaining — end to end

Last updated: 2026-11-01 (after P3–P8). Completed work is in [PROGRESS.md](PROGRESS.md). Hour figures are **estimates**.

## 1. Blockers (no code)

- [ ] Send the coordinator email and get answers on:
  - Is solo submission allowed for the week-6 presentation and the final group project?
  - Is Cloud Lab expected?
  - Do the rubrics mean "deep learning" literally?
- [ ] Get the real due dates for week 6 and exam week.

## 2. Product: still to do

| Item | Why | Est. hours |
|---|---|---|
| Human-label ~30 drafts and calibrate the critic | Live eval: the 7B critic flagged 15 of 16 drafts; whether those flags are right is unknown | 3 |
| Demo recording (2–3 min) and README screenshots | Final-project evidence; screenshot capture was skipped while the browser was in use | 2 |
| Confirm the first GitHub Actions run is green | CI added in P8 but not yet observed on GitHub | 0.5 |
| Accessibility and mobile checks: axe scan, keyboard-only pass, 375 px layout | WCAG 2.2 AA is a spec goal; partly checked by hand | 3 |
| Seasonality-aware features (optional) | All models under-predict peak-season spend | 4 |
| Conformal uncertainty intervals (optional) | Check the MAPIE v1 API first | 3 |
| Remove leftover starter docs and prompts (`prompts/`, old `docs/PRD.md` text) | They describe the original starter, not the built app | 1 |

## 3. Course deliverables

| Deliverable | Weight | What is left | Est. hours |
|---|---|---|---|
| Labs, weeks 2/4/6/8/10 | 30% | One notebook and a 2-page report each, built from: data profile (wk 2), CLV (wk 4), churn (wk 6), product lab (wk 8), scraper (wk 10) | 10 |
| Problems and exercises | 30% | Set in class; add an `exercises/` log | ongoing |
| Week-6 presentation | 10% | Slides from Model lab and Segments | 3 |
| Final project report | 30% | Covers B, C and D with the evidence page as its map, plus a live demo | 8 |
| Reading list | — | Add Hwang (2019), Winston (2014) and Grigsby (2018) to `docs/SOURCES.md` | 1 |

**Total: about 38 hours**, roughly 10 weeks at 4 hours a week, which fits the 12-week term.
