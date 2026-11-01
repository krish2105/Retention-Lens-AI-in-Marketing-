# Data processing agreement: template (draft, not legal advice)

Between **[Customer legal name]** ("Controller") and **[RetentionLens operator legal name]** ("Processor").
To be reviewed by a qualified person before signature. Written with UK GDPR Article 28 and the UAE PDPL in mind.

1. **Subject matter and duration.** Processing of the Controller's invoice data to score trade accounts for
   lapse risk and expected spend, for the pilot period of four weeks and until deletion under clause 9.
2. **Nature and purpose.** Storage, cleaning, statistical modelling and display to the Controller's authorised
   users. No other purpose. No sale of data. No training of models shared with other customers.
3. **Categories of data.** Trade customer account identifiers, invoice numbers, dates, product codes and names,
   quantities, prices, countries. Names and emails of the Controller's users. No special category data.
4. **Data subjects.** The Controller's trade customers (businesses, and sole traders who may be individuals)
   and the Controller's staff who use the service.
5. **Processor obligations.** Act only on documented instructions; ensure staff confidentiality; keep each
   customer's data logically separate (per-workspace `org_id` checks and, on Postgres, row-level security);
   assist with data subject requests; notify personal data breaches without undue delay and within 48 hours.
6. **Security measures.** HTTPS; passwords stored as scrypt hashes; HttpOnly session cookies; role-based access
   (owner, reviewer, viewer); append-only audit log; rate limits; nightly backups with a tested restore;
   dependency and code scanning in CI.
7. **Sub-processors.** Hosting: [Render / Azure / Supabase, region]. Payment (paid plans only): Stripe.
   No third-party AI service: drafting runs on an open model on the Processor's server. The Controller is told
   before any change of sub-processor.
8. **International transfers.** [State region. If outside the UK/UAE, name the transfer mechanism.]
9. **Deletion and return.** The Controller can export and delete everything at any time from the Privacy page.
   At the end of the agreement the Processor deletes the workspace within 30 days, keeping only a deletion
   record without personal data.
10. **Audit.** The Processor provides the information needed to show compliance, including the security
    checklist (`docs/security/ASVS_L1_CHECKLIST.md`) and the latest restore drill report.

Signatures: ______________________ (Controller)   ______________________ (Processor)   Date: ________
