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
| Fill `human_label` in `reports/critic_labels.csv` (16 drafts), then run `calibrate_critic.py score` | The tool and sheet are built; the labels must come from a person | 1 |
| Demo recording (2–3 min) and README screenshots | Final-project evidence; screenshot capture was skipped while the browser was in use | 2 |
| Keyboard-only walkthrough and a screen-reader pass | axe scan (0 violations) and the 375 px layout are done; manual assistive-tech testing is not | 2 |
| Seasonality-aware features (optional) | All models under-predict peak-season spend | 4 |
| Conformal uncertainty intervals (optional) | Check the MAPIE v1 API first | 3 |

## 3. Course deliverables

| Deliverable | Weight | What is left | Est. hours |
|---|---|---|---|
| Labs, weeks 2/4/6/8/10 | 30% | Scaffolds with commands, evidence and rubric headings are in `labs/`; write each analysis yourself | 8 |
| Problems and exercises | 30% | Set in class; add an `exercises/` log | ongoing |
| Week-6 presentation | 10% | Slides from Model lab and Segments | 3 |
| Final project report | 30% | Covers B, C and D with the evidence page as its map, plus a live demo | 8 |

**Total: about 31 hours**, roughly 8 weeks at 4 hours a week. The product is deployed; the rest is the student's own writing, labelling and recording.
