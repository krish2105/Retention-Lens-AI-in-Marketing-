# Gap analysis — RetentionLens vs MAIB AI 208 outline (audit of 2026-11-01)

Basis: `course/outline.docx` read in full (text extracted with Python; no `pandoc` on this machine), every file in the repo read, and the demo/tests/build executed. Labels: **VERIFIED** (observed by running/reading), **ASSUMPTION**, **TODO**.

## 1. What the outline actually requires (VERIFIED from outline.docx)
- Unit: AI in Marketing, MAIB AI 208, core, coordinator Rachit Garg. 2 credit points; 36 timetabled + 84 private-study hours = 120 h (3 h class + 7 h study per week x 12 weeks). Prerequisites: Machine Learning, Marketing Management. Resources: **Cloud Lab access and open-source software**.
- Unit learning outcomes: **A** marketing research + predictive analytics; **B** synthesise traditional, web and social-media data into models of buyer/seller preferences; **C** CLV, churn, retention, identify new customers; **D** implement Generative AI to enhance marketing strategy and decisions.
- Assessment (100%): Problems & Exercises 30% (all sessions; A-D) · Group Project & Classroom Presentation 10% (week 6; A-D) · Laboratory work 30% (weeks 2, 4, 6, 8, 10; A-D) · Final Group Project 30% (exam week; **B, C, D**).
- CLO mapping (2.6): CLO1 knowledge <- A; CLO2 critical/design thinking <- B, C, D; CLO3 communication/team <- C, D (group items only); CLO4 ethics <- D; **CLO5 research methods: "Not Addressed"**.
- Weekly topics: 1 intro · 2 market data plots · 3 predictive analytics for consumer choice · 4 CLV · 5 segmentation/targeting · 6 churn · 7 positioning/new product · 8 brand + pricing · 9 social media/network analysis · 10 competitive intelligence + web scraping · 11 GenAI case studies · 12 final presentation.
- Reading: prescribed Hwang (2019) *Hands-on Data Science for Marketing* (Python/R), chapters per week; recommended Winston (2014), Grigsby (2018); web readings for weeks 8-10.
- Rubrics (Section 3): exercises (understanding, problem-solving, application, clarity); group (content, application of techniques, presentation, team collaboration); labs (implementation, experimentation, problem-solving, reporting); final (research depth, innovation, application of techniques, presentation/reporting).

## 2. What runs today (VERIFIED, 2026-11-01)
| Check | Result |
|---|---|
| `pytest -q services/api/tests` (Python 3.14.7, fresh venv in scratchpad) | 6 passed, 1 deprecation warning (starlette TestClient/httpx) |
| uvicorn + curl: `/api/health`, `/records`, `/summary`, `/domain`, unknown-record review | all as documented; unknown id -> 404 |
| `npm install` + `next build` in `apps/web` (Node v26.10.0) | compiled, type-check OK, 1 static route |
| Contrast (computed from tokens) | accent/page 4.61:1, white-on-accent 4.93:1, dark accent/page 9.07:1, text 14-15:1 — pass AA for body text. `--muted` (#6e7982) not checked. |
| Not run | Browser rendering, theme toggle, mobile layout, keyboard flow, screenshots. **UNTESTED.** |

## 3. Missing against the outline
### 3a. Outcome coverage by the RetentionLens plan
| Outcome | Covered? | Gap |
|---|---|---|
| A research + predictive analytics | Partly (planned) | No predictive model exists; only descriptive RFM on 3 invented transactions. No marketing-research component (survey/market analysis). |
| **B** traditional + web + social sources | **No** | Only one source is planned (UCI Online Retail II, transactional). No web or social-media data, no plan to obtain any with permission. B is explicitly assessed in the 30% final project. |
| C CLV / churn / retention / new customers | Partly (planned) | 90-day repeat purchase is a retention proxy (docs rightly refuse to call it churn ground truth). No CLV calculation, no churn definition, **nothing on identifying new customers** (segmentation/targeting). Nothing built. |
| **D** Generative AI | **No** | Zero GenAI in code, PRD or experiments. "Human-approved campaign draft" is listed in P0 but unimplemented; `prompts/05_RAG_AGENT.md` says to add GenAI only if needed. D is assessed in every component. CLO4 (ethics) is only mapped through D, so it is also unevidenced. |

### 3b. Weekly topics vs repo
Week 2 data plots: **no charts anywhere in the UI** · wk3 predictive: not built · wk4 CLV: not built · wk5 segmentation: absent · wk6 churn: not built · wk7 positioning/NPD, wk8 brand/pricing, wk9 social/network, wk10 competitive intel/web scraping, wk11 GenAI: **absent**.

### 3c. Assessment components with no plan at all
- **Problems & Exercises (30%) and Laboratory work (30%) = 60% of marks** are weekly, in-class/Cloud-Lab work. Nothing in the repo tracks them (no lab folder, no report template, no exercise log). Labs 8 (brand/pricing) and 10 (web scraping) are outside RetentionLens's domain. ASSUMPTION: these are set by the instructor, so they must be done separately from this project — confirm.
- **Group Project & Presentation (10%, week 6)**: outline says group; repo says solo — permission unconfirmed (BLOCKERS). Week 6 = churn topic; with a 10 Nov start that is roughly the week of 15 Dec 2026 (ASSUMPTION: no breaks; calendar dates are not in the outline).
- **Cloud Lab**: the outline lists Cloud Lab access as a requirement; no doc says whether the final project must run there or whether the local FastAPI/Next.js stack is acceptable.
- **Reading list**: Hwang (2019) / Winston / Grigsby are not in `docs/SOURCES.md` or any citation file; no chapter-to-deliverable map.

### 3d. Documentation inconsistencies and template leftovers
- `docs/ASSESSMENT.md` omits the CLO mapping, the weekly-topic map, the Cloud Lab requirement and the 60% of marks that are weekly work (AGENTS.md asks for a course-outcome mapping audit; this file is the first one).
- The outline's rubrics say "deep learning techniques/models" for group, lab and final work although this is a marketing unit — looks like template text; ASK the coordinator. (A neural model in the RQ happens to fit the wording; classical CLV/churn work might not be marked down — unconfirmed.)
- CLO5 is "Not Addressed" in this unit, yet the repo's emphasis is a research question (neural vs GBM vs RFM, frozen tests, ablations, calibration). That depth is not what the rubric rewards most (outcomes A-D); at 4 h/week (~48 h vs 120 nominal) it risks crowding out B and D. This is a recommendation, not a verified fact.
- `prompts/00_MASTER_WORK_PROMPT.md` still contains cross-subject boilerplate (`docs/FINANCE_CLO_COVERAGE.md` does not exist; "If Design Thinking" branch).
- `START_HERE.md` creates the venv in `services/api`; `README.md` creates it at the repo root. Both work, but pick one.
- Not a git repository (`Is a git repository: false`), yet prompts require commits and git commit hashes in run records.
- `docs/UX_DESIGN_SYSTEM.md` dark surface `#162127` vs the CSS `#182328` and a purple dark page `#1E1020`: tokens differ between spec and code.

### 3e. Engineering gaps (VERIFIED by reading code)
- No ML code at all: no pandas/scikit-learn/torch in `requirements.txt`, no feature pipeline, no baselines, no training or evaluation scripts, `research/experiments/` and `data/*` are empty (`.gitkeep` only).
- `project/DATA_SOURCE_REGISTER.csv` is header-only: no dataset downloaded, no checksum, no licence copy. UCI licence/version/schema **unverified** (not fetched this session).
- `domain.py` is 16 lines: no handling of returns/cancellations (the PRD's key import semantics), negative or missing amounts, bad dates (raises `ValueError`), or customer-ID gaps; one unit test. PRD acceptance "zero, boundary and missing-value" tests are not met.
- API: 6 endpoints, unauthenticated, localhost CORS only, SQLite; `/api/demo/import` accepts only the demo schema with `D-` IDs — it is not an invoice importer.
- UI: "Customer cohorts", "Account queue" and "Campaign reviews" render the same generic table (placeholders); no model/methodology view with versions; no pagination/sort; no frontend tests; layout, theme, keyboard use untested in a browser.
- No `research/` write-up, lab reports, viva diary, screenshots, demo recording, or claim-to-evidence map (all listed in `docs/ASSESSMENT.md` as "to create").
- Time: `CURRENT_STATE.md` and `SESSION_LOG.md` show nothing since 2026-10-22; the planned "week A/week B" pre-term work is not logged. Term starts 2026-11-10 (9 days from this audit).

## 4. Decisions needed from the owner (not made here)
1. **Final-project scope:** B and D are required but unplanned. Options: (a) add a permitted web/review text source for B and an LLM-drafted, human-approved outreach component with an ethics/consent evaluation for D; (b) agree a narrower interpretation with the coordinator in writing.
2. **Solo vs group** for the 10% presentation and 30% final project; **Cloud Lab** expectations; "deep learning" wording in rubrics.
3. **How much research depth** (neural vs GBM) to keep given CLO5 is not addressed and hours are limited.

## 5. Suggested next slices (smallest first; none started)
1. Email/ask Rachit Garg the three questions in section 4 (zero code).
2. Verify UCI Online Retail II page (licence, schema, version), then fill `DATA_SOURCE_REGISTER.csv` — needs a human-approved download.
3. Typed invoice loader + returns/cancellation tests in `domain.py` (replaces the 16-line demo) and a data-quality report.
4. RFM + CLV baseline notebook/script and a first chart (serves week 2/4 labs and outcome A/C).
5. Add week-by-week lab/exercise log folder and rubric-aligned report template.
