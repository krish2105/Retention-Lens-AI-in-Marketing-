# Customer discovery interview kit (R1)

For the owner to run. **Claude does not conduct, invent or summarise interviews that did not happen.**
Target: 8–10 conversations with owners, sales managers or account managers at UK or UAE wholesalers and
B2B distributors with 200+ trade accounts. Gate: 8 logged, and 3 or more say they would pilot.

## 1. Screener (2 minutes, by message or at the start of the call)

1. What does your company sell, and to whom? (wholesale / distribution to trade customers → continue)
2. Roughly how many active trade accounts do you have? (under 200 → thank and stop)
3. Who decides which customers get a call or visit each week? (talk to that person)
4. Can you export invoice lines from your accounting or order system? (Sage, Xero, QuickBooks, Unleashed, an ERP)

## 2. Consent (read out, record the answer in the log)

> "I'm a student at [university] building a tool that predicts which trade customers might stop ordering.
> I'd like to ask about how you handle that today. It takes about 30 minutes. I'll take notes; I won't record
> audio unless you say yes. I won't name you or your company in my coursework without written permission,
> and you can stop or withdraw at any time. Is that OK?"

Record: consent yes/no, audio yes/no, may we quote anonymously yes/no.

## 3. Interview guide (30 minutes; ask about the past, not hypotheticals)

**Current behaviour**
1. Tell me about the last time a good customer quietly stopped ordering. When did you notice? What happened next?
2. How do you decide each week who to call or visit? What do you look at?
3. Which tools or reports do you use for that today? What do you like and dislike about them?
4. Roughly how many accounts lapse in a year? How much revenue is that? (their estimate; note it is an estimate)

**Pain and value**
5. If you knew a month earlier that an account was slipping, what would you do differently?
6. Who would act on that list? How much time could they spend on it each week?
7. Have you tried anything to win back lapsed accounts? What worked?

**Trust and data**
8. What would you need to see before trusting a "this account is at risk" score?
9. Would you upload invoice data to a hosted tool? What would stop you?
10. Do you email trade customers about reorders today? Who checks those emails?

**Pricing (Van Westendorp, ask all four, in this order, per month for one sales team)**
11. At what price would this be so cheap you'd doubt the quality?
12. At what price would it be a bargain?
13. At what price would it start to feel expensive, but you'd still consider it?
14. At what price would it be too expensive to consider?

**Close**
15. If we ran a free 4-week pilot on your own data, with a holdout group so we can measure the effect, would you take part? (yes / maybe / no, and why)
16. Who else should I talk to?

## 4. After each interview (same day)

- Copy `research/interviews/TEMPLATE.md` to `research/interviews/I-01.md` (I-02, …) and fill it in.
- Add one row to `research/interviews/log.csv`.
- No names or company names in the repository: use the interview ID. Keep the key in a private note.

## 5. Synthesis (after 6+ interviews; Claude can help structure, the evidence is yours)

- Count how often each pain appears; quote exact words (anonymised).
- Update `docs/research/PERSONAS.md` from hypothesis to evidence, or rewrite it if the interviews disagree.
- Van Westendorp: plot the four cumulative curves; the acceptable range is between "too cheap"/"expensive"
  and "bargain"/"too expensive" crossings. Change `services/api/app/billing.py` PLANS only from this evidence.
