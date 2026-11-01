# Usability test kit (R2 gate)

Gate: **a stranger uploads their own invoices and reaches a scored queue, with a first decision, in under
10 minutes without help, in 4 of 5 sessions.** The owner runs the sessions; results are never invented.

## Participants

5 people who match the personas (owner-manager or account manager at a wholesaler), not classmates who
know the app. Ideally from the interviews. Each brings, or is given, an invoice export (the synthetic sample
`apps/web/public/samples/synthetic_wholesale_invoices.csv` if they cannot share real data).

## Setup (per participant)

1. A fresh workspace: API with `RL_AUTH_MODE=local`; create the participant's account beforehand, or let
   them sign up (that is part of the test).
2. Screen and voice recording only with consent (same consent script as the interview kit).
3. Note the start time. The app records upload, scoring and first-decision times itself: `GET /api/funnel`
   (also shown on the Upload page).

## Script (think aloud; do not help, do not explain the UI)

> "Please say what you are thinking as you go. I'm testing the software, not you. I can't answer questions
> during the tasks, but I will afterwards."

| # | Task | Success when |
|---|---|---|
| 1 | "Upload this invoice file so the tool can look at your customers." | File matched and checked |
| 2 | "Get the list of accounts it thinks you should look at this week." | Scoring finished, queue open |
| 3 | "Pick the account you'd call first and tell me why the tool flagged it." | Opens an account, reads a reason aloud |
| 4 | "Record what you'd do about that account." | A decision is saved |
| 5 | "Draft a short check-in email and decide whether you'd approve it." | Draft created; approves or rejects with a reason |

Record per task: success (yes / with difficulty / no), time, errors, quotes, where they hesitated.

## After the tasks: System Usability Scale (score 1–5, strongly disagree to strongly agree)

1. I think I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think I would need the support of a technical person to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I imagine most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

SUS score = 2.5 × (sum of (odd item − 1) + sum of (5 − even item)). Above 68 is above average.

## Logging

One row per session in `research/usability/log.csv`; notes in `research/usability/U-0X.md` (no names).
After 5 sessions: list the top 3 problems by frequency × severity, fix them, and re-test one person.
