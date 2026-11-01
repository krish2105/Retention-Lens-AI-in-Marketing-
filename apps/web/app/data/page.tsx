"use client";
import { useApi } from "@/lib/api";
import { count } from "@/lib/format";
import { ErrorState, Loading, PageHeader } from "@/components/ui";

type Profile = {
  rows: number; date_min: string; date_max: string; invoices: number; customers: number; countries: number;
  rows_by_sheet: Record<string, number>; issues: Record<string, number>; top_non_product_codes: Record<string, number>;
  customer_model_rows: number; customer_model_customers: number; customer_model_net_value: number;
};
type Source = { name: string; url: string; version: string; access_date: string; license: string; sha256: string; allowed_use: string; notes: string };

const FLAG_LABELS: Record<string, string> = {
  is_cancellation: "Cancellations (invoice starts with C)",
  is_negative_qty: "Negative quantity",
  is_nonpositive_price: "Price zero or below",
  is_non_product: "Non-product codes (postage, fees, vouchers)",
  is_missing_customer: "No customer ID",
  is_duplicate: "Exact duplicate rows",
  negative_qty_not_cancelled: "Negative quantity, not a cancellation",
  duplicate_within_sheet: "Duplicates within one sheet",
  duplicate_across_sheets: "Duplicates across the two sheets (Dec 2010 overlap)",
};

export default function DataPage() {
  const result = useApi<{ profile: Profile; sources: Source[] }>("/api/data");
  const p = result.data?.profile;
  return (
    <>
      <PageHeader eyebrow="Data" title="Where every number starts." lede="One licensed source, checked by checksum, with every problem row flagged and counted rather than silently dropped." />
      {result.error && <section className="glass panel"><ErrorState message={result.error} onRetry={result.reload} /></section>}
      {result.loading && <section className="glass panel"><Loading rows={6} /></section>}
      {p && (
        <>
          <section className="stats">
            <div className="glass stat"><span className="label">Invoice lines</span><span className="value">{count(p.rows)}</span><span className="sub">{p.date_min} to {p.date_max}</span></div>
            <div className="glass stat"><span className="label">Invoices</span><span className="value">{count(p.invoices)}</span><span className="sub">{p.countries} countries</span></div>
            <div className="glass stat"><span className="label">Customers with an ID</span><span className="value">{count(p.customers)}</span><span className="sub">{count(p.customer_model_customers)} usable for models</span></div>
            <div className="glass stat"><span className="label">Rows usable for models</span><span className="value">{count(p.customer_model_rows)}</span><span className="sub">{((100 * p.customer_model_rows) / p.rows).toFixed(1)}% of all lines</span></div>
          </section>
          <div className="row">
            <section className="glass panel" style={{ flex: "1 1 460px" }}>
              <h2>Data-quality flags</h2>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Flag</th><th className="num">Rows</th><th className="num">Share</th></tr></thead>
                  <tbody>
                    {Object.entries(p.issues).filter(([k]) => k !== "rows").map(([k, v]) => (
                      <tr key={k}><td>{FLAG_LABELS[k] ?? k}</td><td className="num">{count(v)}</td><td className="num">{((100 * v) / p.rows).toFixed(1)}%</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <section className="glass panel" style={{ flex: "1 1 340px" }}>
              <h2>Most common non-product codes</h2>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Code</th><th className="num">Rows</th></tr></thead>
                  <tbody>{Object.entries(p.top_non_product_codes).map(([k, v]) => <tr key={k}><td className="mono">{k}</td><td className="num">{count(v)}</td></tr>)}</tbody>
                </table>
              </div>
            </section>
          </div>
          <section className="glass panel">
            <h2>Source register</h2>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Source</th><th>Licence</th><th>Accessed</th><th>SHA-256</th><th>Allowed use</th></tr></thead>
                <tbody>
                  {result.data!.sources.map((s) => (
                    <tr key={s.name}>
                      <td><a href={s.url}>{s.name}</a><div style={{ fontSize: 12, color: "var(--muted)" }}>{s.notes}</div></td>
                      <td>{s.license}</td>
                      <td className="mono">{s.access_date}</td>
                      <td className="mono">{s.sha256 ? `${s.sha256.slice(0, 12)}…` : "—"}</td>
                      <td>{s.allowed_use}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}
