"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { asset, STATIC, type Summary } from "@/lib/api";
import { count, fixed } from "@/lib/format";

const moneyless = (n: number) => new Intl.NumberFormat("en-GB", { notation: "compact", maximumFractionDigits: 2 }).format(n);
import { Icon } from "@/components/ui";
import { Waitlist } from "@/components/Waitlist";

const STEPS = [
  { img: "/img/aur-12a-step-upload.webp", n: "01", title: "Upload your invoices", body: "Drop in a CSV or Excel export from your accounting or order system. Map the columns once; every rejected row is listed, nothing is guessed." },
  { img: "/img/aur-12b-step-predict.webp", n: "02", title: "See who is slipping", body: "Each account gets a 90-day lapse risk, expected spend with a range, and plain reasons: \"no order for 73 days; usual gap 14\"." },
  { img: "/img/aur-12c-step-approve.webp", n: "03", title: "Approve the check-in", body: "A local AI drafts an email from the account's facts only. Checks block invented numbers and pressure. You approve; nothing sends itself." },
];

const DIFFERENT = [
  "Tested honestly: rolling time cutoffs and a frozen test set, scored once. Simpler models won, and we say so.",
  "Built-in proof: a random fifth of each week's queue is held out, so you can see whether contacting accounts actually brings orders back.",
  "Human in charge: every message needs your approval, a recorded consent basis (UK PECR) and passes automatic checks first.",
  "Your data stays yours: one workspace per company, export everything, delete everything, no data used to train shared models.",
];

export default function Landing() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [rows, setRows] = useState<number | null>(null);
  useEffect(() => {
    // Numbers on this page come from the exported run files, like everywhere else.
    fetch(asset("/data/summary.json")).then((r) => (r.ok ? r.json() : null)).then(setSummary).catch(() => setSummary(null));
    fetch(asset("/data/data_profile.json")).then((r) => (r.ok ? r.json() : null)).then((p) => setRows(p?.rows ?? null)).catch(() => setRows(null));
  }, []);
  return (
    <>
      <section className="glass landing-hero">
        <div className="grid" style={{ gap: 16 }}>
          <p className="eyebrow">For wholesalers and B2B distributors</p>
          <h1>Spot the trade accounts that are quietly leaving.</h1>
          <p className="lede">
            RetentionLens reads your invoice history, predicts which accounts will not reorder in the next 90 days and how much spend that puts at risk,
            then helps your team reach out with messages a person approves.
          </p>
          <div className="row" style={{ gap: 10 }}>
            <a className="btn primary" href="#waitlist">Join the pilot waitlist</a>
            <Link className="btn" href="/overview">{STATIC ? "Explore the live demo" : "Open the app"} <Icon name="arrow" /></Link>
          </div>
          <p className="provenance"><span>Pilot stage: no paying customers yet. Prices are a hypothesis we are testing.</span></p>
        </div>
        <div>
          <img className="only-dark" src={asset("/img/aur-11-landing-hero.webp")} alt="" />
          <img className="only-light" src={asset("/img/aur-11-landing-hero-light.webp")} alt="" />
        </div>
      </section>

      <section className="stats" aria-label="Results on the reference dataset">
        <div className="glass stat"><span className="label">Accounts scored in the demo</span><span className="value">{summary ? count(summary.accounts) : "…"}</span><span className="sub">UCI Online Retail II, a real UK wholesaler</span></div>
        <div className="glass stat"><span className="label">Invoice lines checked</span><span className="value">{rows ? moneyless(rows) : "…"}</span><span className="sub">every problem row flagged, none silently dropped</span></div>
        <div className="glass stat"><span className="label">Lapse model PR-AUC, frozen test</span><span className="value tone-healthy">{summary?.frozen_test ? fixed(summary.frozen_test.pr_auc) : "…"}</span><span className="sub">{summary?.frozen_test ? `${count(summary.frozen_test.customers)} customers, cutoff ${summary.frozen_test.cutoff}` : ""}</span></div>
        <div className="glass stat"><span className="label">Emails sent without approval</span><span className="value">0</span><span className="sub">there is no send button, by design</span></div>
      </section>

      <section id="how" className="grid" style={{ gap: 14, scrollMarginTop: 90 }}>
        <div>
          <p className="eyebrow">How it works</p>
          <h2 style={{ fontSize: 28, letterSpacing: -0.8 }}>Three steps, about ten minutes the first time.</h2>
        </div>
        <div className="steps">
          {STEPS.map((s) => (
            <article key={s.n} className="glass step-card">
              <img src={asset(s.img)} alt="" />
              <span className="num-badge">STEP {s.n}</span>
              <h3>{s.title}</h3>
              <p style={{ color: "var(--muted)" }}>{s.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="glass panel">
        <h2>What makes it different</h2>
        <ul className="ticks">
          {DIFFERENT.map((d) => <li key={d}><Icon name="check" /><span>{d}</span></li>)}
        </ul>
      </section>

      <section className="glass split" style={{ padding: 22 }}>
        <div className="grid" style={{ gap: 12, alignContent: "center" }}>
          <p className="eyebrow">Pricing</p>
          <h2 style={{ fontSize: 26 }}>Start with a free four-week pilot.</h2>
          <p className="lede" style={{ marginTop: 0 }}>Pilots run on your own data with a holdout group, so we both learn whether it pays for itself before anyone is billed.</p>
          <div><Link className="btn" href="/pricing">See plans <Icon name="arrow" /></Link></div>
        </div>
        <img src={asset("/img/aur-25-pricing-band.webp")} alt="" />
      </section>

      <section id="waitlist" className="glass panel" style={{ scrollMarginTop: 90 }}>
        <div className="panel-head"><h2>Join the pilot waitlist</h2><span className="hint">we reply within two working days</span></div>
        <p className="lede" style={{ marginTop: 0 }}>We are looking for a few wholesalers with at least a year of invoice history to run a four-week pilot.</p>
        <Waitlist />
      </section>
    </>
  );
}
