"use client";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { apiGet, apiPost, apiUpload, asset, type Me, STATIC, useApi } from "@/lib/api";
import { bytes, count, date, money, pct } from "@/lib/format";
import { EmptyState, ErrorState, PageHeader } from "@/components/ui";

type Mapping = Record<string, string | null>;
type Validation = {
  rows: number; valid_rows: number; rejected_rows: number; customers: number; repeat_customers: number; usable_lines: number;
  date_min: string | null; date_max: string | null; can_score: boolean; blocking: string[]; warnings: string[];
  errors: { row: number; column: string; value: string; problem: string }[]; issues: Record<string, number>;
};
type Dataset = {
  id: string; filename: string; bytes: number; status: string; stage: string | null; pct: number; error: string | null; active: boolean;
  date_order: string; mapping: Mapping | null; duplicate?: boolean;
  inspect: { rows: number; headers: string[]; suggested_mapping: Mapping; problems: string[]; sample: Record<string, string>[] } | null;
  validation: Validation | null;
  summary: { accounts: number; bands: Record<string, number>; value_at_risk_high: number; scoring_cutoff: string; drift?: { psi: number | null; note: string }; intervals?: { available: boolean; calibration_coverage?: number } } | null;
};
type Row = Pick<Dataset, "id" | "filename" | "bytes" | "status" | "stage" | "pct" | "active"> & { created_at: string; created_by: string };

const FIELDS: { key: string; label: string; required: boolean }[] = [
  { key: "customer_id", label: "Customer or account ID", required: true },
  { key: "invoice", label: "Invoice or order number", required: true },
  { key: "invoice_date", label: "Invoice date", required: true },
  { key: "quantity", label: "Quantity", required: true },
  { key: "price", label: "Unit price", required: true },
  { key: "stock_code", label: "Product code", required: false },
  { key: "description", label: "Product name", required: false },
  { key: "country", label: "Country", required: false },
];
const STAGES = ["Upload", "Match columns", "Check", "Score"];
const STAGE_LABEL: Record<string, string> = { queued: "Waiting for the scoring worker", starting: "Starting", reading: "Reading the file", validating: "Checking rows", preparing: "Building purchase histories", fitting: "Fitting BG/NBD and Gamma-Gamma", segmenting: "Naming segments and value ranges", writing: "Saving results", done: "Done" };

export default function UploadPage() {
  const me = useApi<Me>("/api/auth/me");
  const list = useApi<Row[]>("/api/datasets");
  const [ds, setDs] = useState<Dataset | null>(null);
  const [mapping, setMapping] = useState<Mapping>({});
  const [dateOrder, setDateOrder] = useState("auto");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [over, setOver] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const canEdit = me.data ? me.data.role !== "viewer" : false;

  const load = useCallback(async (id: string) => {
    const next = await apiGet<Dataset>(`/api/datasets/${id}`);
    setDs(next);
    setMapping(next.mapping ?? next.inspect?.suggested_mapping ?? {});
    setDateOrder(next.date_order ?? "auto");
    return next;
  }, []);

  // Poll while the background job runs.
  useEffect(() => {
    if (!ds || !["queued", "scoring"].includes(ds.status)) return;
    const timer = window.setInterval(() => {
      load(ds.id).then((next) => { if (!["queued", "scoring"].includes(next.status)) list.reload(); }).catch(() => undefined);
    }, 1500);
    return () => window.clearInterval(timer);
  }, [ds, load, list]);

  const run = async (action: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const upload = (file: File | undefined) => file && run(async () => {
    const result = await apiUpload<Dataset>(`/api/datasets?filename=${encodeURIComponent(file.name)}`, file);
    setDs(result);
    setMapping(result.mapping ?? result.inspect?.suggested_mapping ?? {});
    list.reload();
  });
  const validate = () => ds && run(async () => setDs(await apiPost<Dataset>(`/api/datasets/${ds.id}/validate`, { mapping, date_order: dateOrder })));
  const score = () => ds && run(async () => setDs(await apiPost<Dataset>(`/api/datasets/${ds.id}/score`, {})));
  const remove = (id: string) => run(async () => {
    if (!window.confirm("Delete this upload and its scores? This cannot be undone.")) return;
    await apiPost(`/api/datasets/${id}/delete`, {});
    if (ds?.id === id) setDs(null);
    list.reload();
    me.reload();
  });
  const activate = (id: string) => run(async () => { await apiPost(`/api/datasets/${id}/activate`, {}); list.reload(); me.reload(); });
  const toggleSample = () => me.data && run(async () => { await apiPost("/api/org/sample", { enabled: !me.data!.org.use_sample }); me.reload(); });

  const stage = !ds ? 0 : ["uploaded"].includes(ds.status) ? 1 : ["validated", "needs_fixes"].includes(ds.status) ? 2 : 3;
  const v = ds?.validation;

  return (
    <>
      <PageHeader eyebrow="Upload data" title="Score your own invoices." lede="Upload a CSV or Excel export with one row per invoice line. You match the columns, see every row that could not be read, and get a scored weekly queue. Files stay in this workspace." />
      {STATIC && <section className="glass panel"><EmptyState image="/img/aur-15-dropzone.webp" title="Uploads need the full app" body="This public demo is read-only. Run RetentionLens locally (or on the hosted server) to upload invoices. You can still download the synthetic sample file to see the expected shape." action={<a className="btn" href={asset("/samples/synthetic_wholesale_invoices.csv")} download>Download the synthetic sample</a>} /></section>}

      {!STATIC && (
        <section className="glass panel">
          <ol className="wizard-steps" aria-label="Progress">
            {STAGES.map((label, i) => <li key={label} aria-current={i === stage ? "step" : undefined} className={i < stage ? "done" : undefined}>{i + 1}. {label}</li>)}
          </ol>
          {error && <p className="toast error" role="alert">{error}</p>}

          {!ds && (
            <div className="dropzone" data-over={over}
              onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
              onDrop={(e) => { e.preventDefault(); setOver(false); if (canEdit) upload(e.dataTransfer.files[0]); }}>
              <img src={asset("/img/aur-15-dropzone.webp")} alt="" />
              <strong style={{ color: "var(--ink)" }}>Drop a .csv or .xlsx file here</strong>
              <span>Up to 50 MB. Needs customer ID, invoice number, date, quantity and unit price. At least 30 customers and 90 days of history.</span>
              <input ref={input} type="file" accept=".csv,.xlsx,.xlsm,.tsv,.txt" className="sr-only" id="file" onChange={(e) => upload(e.target.files?.[0])} disabled={!canEdit || busy} />
              <div className="row" style={{ gap: 8, justifyContent: "center" }}>
                <label htmlFor="file" className="btn primary" aria-disabled={!canEdit || busy}>{busy ? "Uploading…" : "Choose a file"}</label>
                <a className="btn" href={asset("/samples/synthetic_wholesale_invoices.csv")} download>Try the synthetic sample</a>
              </div>
              {!canEdit && me.data && <span>Viewers cannot upload. Ask a workspace owner for the reviewer role.</span>}
            </div>
          )}

          {ds && ds.duplicate && <p className="notice">You uploaded this exact file before, so the existing import was reopened instead of creating a copy.</p>}

          {ds && stage === 1 && ds.inspect && (
            <div className="grid" style={{ gap: 14 }}>
              <div className="panel-head"><h2>Match your columns</h2><span className="hint">{ds.filename} · {count(ds.inspect.rows)} rows · {bytes(ds.bytes)}</span></div>
              <div className="mapping">
                {FIELDS.map((f) => (
                  <label key={f.key} className="field">{f.label}{f.required ? "" : " (optional)"}
                    <select value={mapping[f.key] ?? ""} onChange={(e) => setMapping({ ...mapping, [f.key]: e.target.value || null })}>
                      <option value="">{f.required ? "Choose a column…" : "Not in my file"}</option>
                      {ds.inspect!.headers.map((h) => <option key={h} value={h}>{h}</option>)}
                    </select>
                  </label>
                ))}
                <label className="field">Date format
                  <select value={dateOrder} onChange={(e) => setDateOrder(e.target.value)}>
                    <option value="auto">Detect (assume day first if unclear)</option>
                    <option value="dayfirst">Day first: 31/01/2025</option>
                    <option value="monthfirst">Month first: 01/31/2025</option>
                  </select>
                </label>
              </div>
              {ds.inspect.sample.length > 0 && (
                <details className="twin"><summary>Preview the first rows</summary>
                  <div className="table-wrap" tabIndex={0} role="region" aria-label="File preview">
                    <table><thead><tr>{ds.inspect.headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
                      <tbody>{ds.inspect.sample.map((r, i) => <tr key={i}>{ds.inspect!.headers.map((h) => <td key={h}>{r[h]}</td>)}</tr>)}</tbody></table>
                  </div>
                </details>
              )}
              <div className="row" style={{ gap: 8 }}>
                <button className="btn primary" type="button" onClick={validate} disabled={busy || !canEdit}>{busy ? "Checking…" : "Check the file"}</button>
                <button className="btn" type="button" onClick={() => setDs(null)}>Upload a different file</button>
              </div>
            </div>
          )}

          {ds && v && stage === 2 && (
            <div className="split">
              <img src={asset(v.can_score ? "/img/aur-16-validated.webp" : "/img/aur-17-needs-fixes.webp")} alt="" />
              <div className="grid" style={{ gap: 12 }}>
                <h2>{v.can_score ? "Your file is ready to score" : "This file needs fixes before scoring"}</h2>
                <div className="kv">
                  <div><span>Rows read</span><strong>{count(v.rows)}</strong></div>
                  <div><span>Rows rejected</span><strong className={v.rejected_rows ? "tone-high" : undefined}>{count(v.rejected_rows)}</strong></div>
                  <div><span>Customers with a sale</span><strong>{count(v.customers)}</strong></div>
                  <div><span>Ordered on 2+ days</span><strong>{count(v.repeat_customers)}</strong></div>
                  <div><span>From</span><strong>{date(v.date_min)}</strong></div>
                  <div><span>To</span><strong>{date(v.date_max)}</strong></div>
                </div>
                {v.blocking.map((b) => <p key={b} className="toast error">{b}</p>)}
                {v.warnings.map((w) => <p key={w} className="notice">{w}</p>)}
                <p className="provenance"><span>Flagged, not dropped: {count(v.issues.is_cancellation)} cancellations · {count(v.issues.is_duplicate)} duplicates · {count(v.issues.is_non_product)} postage/fee lines · {count(v.issues.is_missing_customer)} without a customer</span></p>
                <div className="row" style={{ gap: 8 }}>
                  {v.can_score && <button className="btn primary" type="button" onClick={score} disabled={busy || !canEdit}>Score {count(v.customers)} accounts</button>}
                  <button className="btn" type="button" onClick={() => setDs({ ...ds, status: "uploaded" })}>Change the column matching</button>
                </div>
              </div>
            </div>
          )}
          {ds && v && stage === 2 && v.errors.length > 0 && (
            <details className="twin" open={!v.can_score}><summary>{count(v.rejected_rows)} rows could not be read (first {v.errors.length} problems shown)</summary>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Rejected rows">
                <table><thead><tr><th>Row</th><th>Column</th><th>Value</th><th>Problem</th></tr></thead>
                  <tbody>{v.errors.map((e, i) => <tr key={i}><td className="mono">{e.row}</td><td>{e.column}</td><td className="mono">{e.value}</td><td>{e.problem}</td></tr>)}</tbody></table>
              </div>
            </details>
          )}

          {ds && stage === 3 && (
            <div className="split">
              <img src={asset(ds.status === "ready" ? "/img/aur-19-all-done.webp" : "/img/aur-18-scoring.webp")} alt="" />
              <div className="grid" style={{ gap: 12, alignContent: "center" }} aria-live="polite">
                {ds.status === "failed" ? (
                  <>
                    <h2>Scoring failed</h2>
                    <p className="toast error">{ds.error}</p>
                    <div><button className="btn primary" type="button" onClick={score} disabled={busy}>Try again</button></div>
                  </>
                ) : ds.status === "ready" && ds.summary ? (
                  <>
                    <h2>Scored {count(ds.summary.accounts)} accounts</h2>
                    <div className="kv">
                      <div><span>High risk</span><strong className="tone-high">{count(ds.summary.bands.high)}</strong></div>
                      <div><span>Spend at risk (high)</span><strong>{money(ds.summary.value_at_risk_high)}</strong></div>
                      <div><span>Scored as of</span><strong>{date(ds.summary.scoring_cutoff)}</strong></div>
                      <div><span>Value ranges</span><strong>{ds.summary.intervals?.available ? `${pct(ds.summary.intervals.calibration_coverage ?? null)} coverage` : "Not enough history"}</strong></div>
                    </div>
                    {ds.summary.drift && <p className="provenance"><span>Change against the previous upload: {ds.summary.drift.psi == null ? ds.summary.drift.note : `PSI ${ds.summary.drift.psi} (${ds.summary.drift.note})`}</span></p>}
                    <div className="row" style={{ gap: 8 }}>
                      <Link className="btn primary" href="/queue">Open this week&apos;s queue</Link>
                      <Link className="btn" href="/accounts">See all accounts</Link>
                      <button className="btn" type="button" onClick={() => setDs(null)}>Upload another file</button>
                    </div>
                  </>
                ) : (
                  <>
                    <h2>Scoring your accounts…</h2>
                    <div className="progress" role="progressbar" aria-valuenow={ds.pct} aria-valuemin={0} aria-valuemax={100} aria-label="Scoring progress"><span style={{ width: `${Math.max(ds.pct, 4)}%` }} /></div>
                    <p style={{ color: "var(--muted)" }}>{STAGE_LABEL[ds.stage ?? "queued"] ?? ds.stage} · {ds.pct}%. You can leave this page; scoring carries on.</p>
                  </>
                )}
              </div>
            </div>
          )}
        </section>
      )}

      {!STATIC && (
        <section className="glass panel">
          <div className="panel-head"><h2>Uploads in this workspace</h2>
            {me.data && me.data.role === "owner" && (
              <button className="btn" type="button" onClick={toggleSample} disabled={busy}>{me.data.org.use_sample ? "Hide the sample dataset" : "Load the sample dataset"}</button>
            )}
          </div>
          {list.error && <ErrorState message={list.error} onRetry={list.reload} />}
          {list.data && list.data.length === 0 && <p style={{ color: "var(--muted)" }}>No uploads yet. {me.data?.org.use_sample ? "You are looking at the UCI sample dataset." : ""}</p>}
          {list.data && list.data.length > 0 && (
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Uploads">
              <table>
                <thead><tr><th>File</th><th>Status</th><th>Uploaded</th><th>By</th><th></th></tr></thead>
                <tbody>
                  {list.data.map((r) => (
                    <tr key={r.id}>
                      <td><button className="row-btn" type="button" onClick={() => load(r.id)}>{r.filename}</button> <span className="mono" style={{ color: "var(--muted)" }}>{bytes(r.bytes)}</span></td>
                      <td>{r.active ? <span className="badge">Active</span> : r.status.replace("_", " ")}</td>
                      <td>{date(r.created_at)}</td>
                      <td>{r.created_by}</td>
                      <td className="row" style={{ gap: 6 }}>
                        {r.status === "ready" && !r.active && canEdit && <button className="btn" type="button" onClick={() => activate(r.id)}>Make active</button>}
                        {me.data?.role === "owner" && <button className="btn danger" type="button" onClick={() => remove(r.id)}>Delete</button>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </>
  );
}
