"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { apiPost, asset, type Me, useApi } from "@/lib/api";
import { count, pct } from "@/lib/format";
import { ErrorState, PageHeader } from "@/components/ui";

type Plan = { name: string; price_gbp_month: number; max_accounts: number; seats: number; note: string };
type Billing = { plan: string; limits: Plan | null; usage: { active_accounts: number; share: number | null }; billing_configured: boolean; note: string; status: string };

export default function BillingPage() {
  return <Suspense><BillingInner /></Suspense>;
}

function BillingInner() {
  const params = useSearchParams();
  const me = useApi<Me>("/api/auth/me");
  const billing = useApi<Billing>("/api/billing");
  const plans = useApi<{ plans: Record<string, Plan> }>("/api/plans");
  const [error, setError] = useState<string | null>(null);
  const b = billing.data;
  const checkout = async (plan: string) => {
    setError(null);
    try {
      const { url } = await apiPost<{ url: string }>("/api/billing/checkout", { plan });
      window.location.assign(url);
    } catch (e) {
      setError((e as Error).message);
    }
  };
  return (
    <>
      <PageHeader eyebrow="Workspace" title="Plan and billing." lede="Your plan, what you are using, and upgrades through Stripe Checkout in test mode." />
      {params.get("checkout") === "success" && <p className="toast ok" role="status">Test checkout complete. The plan updates when Stripe confirms the payment by webhook.</p>}
      {params.get("checkout") === "cancelled" && <p className="toast" role="status">Checkout cancelled; nothing changed.</p>}
      <section className="glass split" style={{ padding: 22 }}>
        <div className="grid" style={{ gap: 12, alignContent: "center" }}>
          {billing.error && <ErrorState message={billing.error} onRetry={billing.reload} />}
          {b && (
            <>
              <p className="eyebrow">Current plan</p>
              <h2 style={{ fontSize: 30 }}>{plans.data?.plans[b.plan]?.name ?? b.plan}</h2>
              <div className="kv">
                <div><span>Active accounts</span><strong>{count(b.usage.active_accounts)}</strong>{b.limits && <span>of {count(b.limits.max_accounts)} ({pct(b.usage.share)})</span>}</div>
                <div><span>Billing</span><strong className={b.billing_configured ? "tone-healthy" : "tone-watch"}>{b.billing_configured ? "Test mode" : "Not set up"}</strong><span>{b.note}</span></div>
              </div>
              {b.limits && <div className="progress" role="progressbar" aria-label="Account allowance used" aria-valuenow={Math.round((b.usage.share ?? 0) * 100)} aria-valuemin={0} aria-valuemax={100}><span style={{ width: `${Math.min(100, (b.usage.share ?? 0) * 100)}%` }} /></div>}
              <p className="notice">{b.status}. No real card is ever charged by this build: only Stripe test keys are accepted, and test card numbers are used in checkout.</p>
            </>
          )}
        </div>
        <img src={asset("/img/aur-20-plans.webp")} alt="" />
      </section>
      {error && <p className="toast error" role="alert">{error}</p>}
      {plans.data && (
        <section className="plans" aria-label="Change plan">
          {Object.entries(plans.data.plans).map(([key, plan]) => (
            <article key={key} className={`glass plan ${b?.plan === key ? "featured" : ""}`}>
              <h3>{plan.name}</h3>
              <p className="price">{plan.price_gbp_month ? `£${plan.price_gbp_month}` : "Free"}</p>
              <p style={{ color: "var(--muted)" }}>Up to {count(plan.max_accounts)} accounts · {plan.seats} seats</p>
              <div style={{ marginTop: "auto" }}>
                {b?.plan === key ? <span className="badge">Current plan</span> : key === "pilot" ? <Link className="btn" href="/#waitlist">Apply for a pilot</Link> : (
                  <button className="btn primary" type="button" disabled={me.data?.role !== "owner" || !b?.billing_configured} onClick={() => checkout(key)}>Upgrade (test mode)</button>
                )}
              </div>
            </article>
          ))}
        </section>
      )}
    </>
  );
}
