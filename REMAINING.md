# What is remaining — end to end

Last updated: 2026-11-01. Completed work is in [PROGRESS.md](PROGRESS.md). Hour figures are **estimates** for planning, not measurements.

## 1. Blockers to clear first (no code)

- [ ] Send the coordinator email (draft exists) and get answers on:
  - Is solo submission allowed for the week-6 presentation and the final group project?
  - Must the work be built or submitted in Cloud Lab?
  - Do the rubrics mean "deep learning" literally?
  - How deep must outcomes B and D go?
- [ ] Get the real due dates for the week-6 presentation and the exam-week final project.

## 2. Product build (spec phases P3–P8)

| Phase | What is left | Outline link | Est. hours |
|---|---|---|---|
| **P3** API + Aurora UI shell | FastAPI endpoints over P2 run files; Next.js Aurora shell with light/dark/system theme; Overview and Accounts screens showing real run values with data-source footers; empty, loading and error states; images compressed into `assets/generated/` | A, C | 12 |
| **P4** Segments | RFM clusters; 3D customer galaxy (React Three Fiber) with a table version and a 2D fallback; lookalike scoring to find new customers like the best ones | C (new customers), week 5 | 8 |
| **P5** Signals | Wikipedia pageviews, GDELT and a Google Trends CSV; co-purchase network; synthetic social posts labelled SYNTHETIC; scraping demo on toscrape.com; a licence row for each source | **B**, weeks 9–10 | 8 |
| **P6** Outreach studio | Ollama `qwen2.5:7b` drafts through read-only tools; a checker that blocks unsupported numbers; a critic pass; a human approval gate; no send tool; consent field; audit log; tests and red-team suite run in CI | **D**, CLO4, week 11 | 12 |
| **P7** Product and pricing lab | Market-basket rules; price elasticity, labelled as association rather than cause; positioning notes | Weeks 7–8 | 5 |
| **P8** Finish | Professional README with banner, real metrics table and image disclosure; Course evidence page; demo recording; clean-machine run check | All | 6 |

Optional (only if time allows): seasonality features (P2b), conformal uncertainty intervals (check the MAPIE v1 API first), a ZILN neural model (not supported by current evidence).

## 3. Course deliverables

| Deliverable | Weight | What is left | Est. hours |
|---|---|---|---|
| Labs, weeks 2/4/6/8/10 | 30% | One notebook and a 2-page report each (implementation, experimentation, problem-solving, reporting). Weeks 4 and 6 can reuse P2 results; weeks 8 and 10 need P7 and P5. | 15 |
| Problems and exercises, every session | 30% | Set by the instructor; not tracked in the repo yet. Add an `exercises/` log. | ongoing |
| Week-6 group presentation | 10% | Slides from the P2 churn and CLV results, with charts | 4 |
| Final group project, exam week | 30% | Report covering outcomes B, C and D, live demo, reproducible run | 10 |
| Reading | — | Add Hwang (2019), Winston (2014) and Grigsby (2018) to `docs/SOURCES.md` and map chapters to weeks | 1 |

## 4. Engineering and housekeeping

- [ ] Replace the starter demo API and dashboard with P3 (the old `services/api` demo code remains).
- [ ] Add GitHub Actions running the ML tests, API tests, web build and accessibility (axe) checks.
- [ ] Compress the 11 final images to WebP under 400 KB and add them to `assets/generated/`. Keep the 36 MB collection and its zip out of git.
- [ ] Clean template leftovers in `prompts/00_MASTER_WORK_PROMPT.md` and `docs/ASSESSMENT.md`.
- [ ] Charts for week 2 (market data plots): none exist yet.

## 5. Time check

The remaining build (P3–P8) is about 51 hours, and course deliverables add roughly 30 more, for **about 80 hours** in total. At the planned 4 hours a week, that is about **20 weeks**, while the term is 12. Options: raise this project's weekly share, cut P7 and the optional items, or reuse build work directly as lab reports.
