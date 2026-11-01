"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { asset, type Summary } from "@/lib/api";
import { count, fixed, pct } from "@/lib/format";

type R5 = { summary: { seasonal_bias_reduction_dev: number; interval_coverage_dev: number[]; post_hoc_peak_gap_closed?: number; ziln_vs_bgnbd: { lapse_pr_auc: { wins: number; of: number } } } };
type Load = { users: number; seconds: number; requests: number; errors: number; p95_ms: number; meets_slo: boolean };
type Lookalikes = { test_auc: number; test_customers: number };

function useJson<T>(name: string) {
  const [data, setData] = useState<T | null>(null);
  useEffect(() => {
    fetch(asset(`/data/${name}.json`)).then((r) => (r.ok ? r.json() : null)).then(setData).catch(() => setData(null));
  }, [name]);
  return data;
}

/** Portfolio case study. Every number is read from an exported run file; the pilot section stays empty until a pilot happens. */
export default function CaseStudy() {
  const summary = useJson<Summary>("summary");
  const profile = useJson<{ rows: number }>("data_profile");
  const r5 = useJson<R5>("r5");
  const load = useJson<Load>("load_test");
  const look = useJson<Lookalikes>("lookalikes");
  const f = summary?.frozen_test;
  return (
    <>
      <section className="glass split" style={{ padding: 24 }}>
        <div className="grid" style={{ gap: 12, alignContent: "center" }}>
          <p className="eyebrow">Case study · MAIB AI 208 · AI in Marketing</p>
          <h1>Predicting which trade accounts will stop ordering, and proving whether outreach helps.</h1>
          <p className="lede">A solo build: from 2009–2011 invoices of a real UK wholesaler to a multi-tenant product with self-serve upload, a weekly review queue with a random holdout, and AI-drafted outreach a person must approve.</p>
        </div>
        <img src={asset("/img/aur-26-case-study.webp")} alt="" />
      </section>

      <section className="stats" aria-label="Results">
        <div className="glass stat"><span className="label">Invoice lines, flagged not dropped</span><span className="value">{profile ? count(profile.rows) : "…"}</span><span className="sub">UCI Online Retail II, CC BY 4.0</span></div>
        <div className="glass stat"><span className="label">Lapse PR-AUC, frozen test</span><span className="value tone-healthy">{f ? fixed(f.pr_auc) : "…"}</span><span className="sub">{f ? `${count(f.customers)} customers, scored once at ${f.cutoff}` : ""}</span></div>
        <div className="glass stat"><span className="label">Value ranking Gini, frozen test</span><span className="value">{f ? fixed(f.value_gini) : "…"}</span><span className="sub">BG/NBD + Gamma-Gamma</span></div>
        <div className="glass stat"><span className="label">Lookalike AUC, new customers</span><span className="value">{look ? fixed(look.test_auc) : "…"}</span><span className="sub">{look ? `${count(look.test_customers)} later customers, time-based split` : ""}</span></div>
      </section>

      <section className="glass panel prose" style={{ maxWidth: "none" }}>
        <h2>The problem</h2>
        <p>Wholesalers lose trade accounts quietly: no complaint, just no next order. By the time a monthly report shows it, the buyer has moved on. The job: an early, short list of accounts worth a call, with reasons a salesperson can say out loud, and a way to tell whether the calls work.</p>
        <h2>What was decided, and why</h2>
        <ul>
          <li><strong>Evaluation first.</strong> Four rolling time cutoffs and a frozen test, fixed before any result. Simple probabilistic models (BG/NBD + Gamma-Gamma) beat LightGBM, so the simple model serves.</li>
          <li><strong>Seasonality.</strong> The plain model over-predicted spend after Christmas and under-predicted before it. A seasonal multiplier cut total-spend bias by {r5 ? pct(r5.summary.seasonal_bias_reduction_dev) : "…"} on the development cutoffs{r5?.summary.post_hoc_peak_gap_closed != null ? ` (${pct(r5.summary.post_hoc_peak_gap_closed)} on the peak window, post hoc)` : ""}.</li>
          <li><strong>Honest uncertainty.</strong> 80% value ranges by split conformal prediction covered {r5 ? r5.summary.interval_coverage_dev.map((c) => pct(c, 1)).join(", ") : "…"} of accounts on the development cutoffs.</li>
          <li><strong>A deep-learning challenger that lost.</strong> A zero-inflated lognormal network won {r5 ? `${r5.summary.ziln_vs_bgnbd.lapse_pr_auc.wins} of ${r5.summary.ziln_vs_bgnbd.lapse_pr_auc.of}` : "…"} development cutoffs on lapse PR-AUC, so it was not adopted. Two fixes made after seeing dev results are disclosed.</li>
          <li><strong>Proof built in.</strong> A random fifth of each weekly queue is held out, so reorder rates of contacted and untouched accounts can be compared with a confidence interval.</li>
          <li><strong>AI with a leash.</strong> Only structured facts reach the local model; checks block invented numbers, offers, pressure, links and leaks; nothing can be sent from the product.</li>
        </ul>
        <h2>Engineering evidence</h2>
        <ul>
          <li>Two-tenant isolation tests, roles, invites, export and delete-my-workspace; Postgres row-level security migration prepared.</li>
          <li>Load test: {load ? `${count(load.requests)} requests from ${load.users} simulated reviewers in ${load.seconds} s, ${load.errors} errors, p95 ${load.p95_ms} ms (${load.meets_slo ? "SLO met" : "SLO missed"})` : "…"}. It caught a write-lock bug in the weekly queue, now fixed.</li>
          <li>Backups with a restore drill, structured logs, metrics, a public status page, OWASP LLM red-team tests in CI.</li>
        </ul>
        <h2>Pilot results</h2>
        <p className="notice">Not run yet. This section will report the contacted vs held-out reorder rates from a real four-week pilot, with the customer&apos;s written permission, or say plainly that there is none.</p>
        <h2>Limitations</h2>
        <ul>
          <li>One dataset from one company, 2009–2011. Behaviour today may differ.</li>
          <li>Interviews, usability sessions and a pilot have not happened yet; pricing is a hypothesis.</li>
          <li>The AI critic is not yet calibrated against human labels.</li>
        </ul>
        <p className="provenance"><span>Sources: summary.json, data_profile.json, r5.json, load_test.json, lookalikes.json in the public demo data</span><span><Link href="/model-lab">Model lab</Link></span><span><a href="https://github.com/krish2105/Retention-Lens-AI-in-Marketing-">Repository</a></span></p>
      </section>
    </>
  );
}
