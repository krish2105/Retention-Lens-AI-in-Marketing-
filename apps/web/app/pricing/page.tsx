"use client";
import Link from "next/link";
import { asset, useApi } from "@/lib/api";
import { count } from "@/lib/format";
import { ErrorState, Icon, Loading } from "@/components/ui";

type Plan = { name: string; price_gbp_month: number; max_accounts: number; seats: number; note: string };
type Plans = { plans: Record<string, Plan>; status: string; currency: string };

const FEATURES = ["Upload CSV or Excel, scored in minutes", "Weekly review queue with a random holdout", "Lapse risk, expected spend and value ranges", "AI-drafted, human-approved outreach", "Audit log, export and delete-my-data"];
const FAQ = [
  ["Why is there a free pilot?", "Because the tool should prove itself on your data first. A random holdout group shows whether contacted accounts reorder more than similar ones left alone."],
  ["Do you send emails for us?", "No. RetentionLens drafts and you approve. Approved drafts are exported for your own email system, which keeps consent and unsubscribe handling with you."],
  ["Where does the AI run?", "Drafting uses an open model running on the server, not a third-party chat service. Only structured facts about an account go into the prompt, never free text from your files."],
  ["How did you pick these prices?", "They are a starting hypothesis. We test them in customer interviews with four price questions (Van Westendorp) and will change them if the evidence says so."],
];

export default function Pricing() {
  const plans = useApi<Plans>("/api/plans");
  return (
    <>
      <section className="glass split" style={{ padding: 24 }}>
        <div className="grid" style={{ gap: 12, alignContent: "center" }}>
          <p className="eyebrow">Pricing</p>
          <h1>Pay for accounts you keep, not for seats you don&apos;t use.</h1>
          <p className="lede">Plans are sized by active trade accounts. Every plan includes the full product.</p>
          <p className="notice">{plans.data?.status ?? "Pricing hypothesis: not yet validated with customers"}. Paid plans run through Stripe in test mode only; no real card is charged.</p>
        </div>
        <img src={asset("/img/aur-25-pricing-band.webp")} alt="" />
      </section>
      {plans.loading && <Loading />}
      {plans.error && <ErrorState message={plans.error} onRetry={plans.reload} />}
      {plans.data && (
        <section className="plans" aria-label="Plans">
          {Object.entries(plans.data.plans).map(([key, plan]) => (
            <article key={key} className={`glass plan ${key === "starter" ? "featured" : ""}`}>
              <h2>{plan.name}</h2>
              <p className="price">{plan.price_gbp_month === 0 ? "Free" : `£${plan.price_gbp_month}`}<small style={{ fontSize: 14, color: "var(--muted)" }}>{plan.price_gbp_month ? " / month" : " for 4 weeks"}</small></p>
              <p style={{ color: "var(--muted)" }}>{plan.note}</p>
              <ul>
                <li><Icon name="check" />Up to {count(plan.max_accounts)} active accounts</li>
                <li><Icon name="check" />{plan.seats} team seats</li>
                {FEATURES.map((f) => <li key={f}><Icon name="check" />{f}</li>)}
              </ul>
              <div style={{ marginTop: "auto" }}>
                {key === "pilot" ? <Link className="btn primary" href="/#waitlist">Apply for a pilot</Link> : <Link className="btn" href="/billing">Choose {plan.name}</Link>}
              </div>
            </article>
          ))}
        </section>
      )}
      <section className="glass panel">
        <h2>Questions</h2>
        {FAQ.map(([q, a]) => (
          <details key={q} className="twin">
            <summary style={{ color: "var(--ink)", fontWeight: 600, padding: "6px 0" }}>{q}</summary>
            <p style={{ color: "var(--muted)", paddingBottom: 8 }}>{a}</p>
          </details>
        ))}
      </section>
    </>
  );
}
