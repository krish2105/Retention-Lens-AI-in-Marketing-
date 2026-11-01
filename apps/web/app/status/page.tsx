"use client";
import { asset, useApi } from "@/lib/api";
import { ErrorState, Loading } from "@/components/ui";

type Status = {
  status: string; static?: boolean; components: Record<string, { ok: boolean; detail?: string; by_status?: Record<string, number> }>;
  uptime_seconds: number | null; worst_read_p95_ms: number | null; slo: { read_p95_ms: number; availability: number; scoring_100k_lines_minutes: number }; auth_mode: string; version: string;
};
const NAMES: Record<string, string> = { database: "Database", reference_data: "Reference dataset", scoring_worker: "Scoring worker", jobs: "Scoring jobs", local_ai: "Local AI model", static_snapshot: "Static snapshot", api: "Live API" };

export default function StatusPage() {
  const status = useApi<Status>("/api/status");
  const s = status.data;
  return (
    <>
      <section className="glass split" style={{ padding: 24 }}>
        <div className="grid" style={{ gap: 12, alignContent: "center" }}>
          <p className="eyebrow">System status</p>
          <h1>{s ? (s.static ? "Public demo: static snapshot" : s.status === "operational" ? "All core systems operational" : "Some systems degraded") : "Checking…"}</h1>
          <p className="lede">Live checks from the API, refreshed when you load this page. Targets below are service level objectives we measure against, not guarantees.</p>
        </div>
        <img src={asset("/img/aur-24-status.webp")} alt="" />
      </section>
      <section className="glass panel">
        <h2>Components</h2>
        {status.loading && <Loading />}
        {status.error && <ErrorState message={status.error} onRetry={status.reload} />}
        {s && (
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Components">
            <table>
              <tbody>
                {Object.entries(s.components).map(([key, c]) => (
                  <tr key={key}>
                    <td><span className={`status-dot ${c.ok ? "ok" : "bad"}`} aria-hidden="true" /><strong>{NAMES[key] ?? key}</strong></td>
                    <td>{c.ok ? "OK" : "Unavailable"}</td>
                    <td style={{ color: "var(--muted)" }}>{c.detail ?? (c.by_status ? Object.entries(c.by_status).map(([k, v]) => `${v} ${k}`).join(" · ") || "No jobs yet" : "")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {s && (
        <section className="glass panel">
          <h2>Service level objectives</h2>
          <div className="kv">
            <div><span>Read requests, 95th percentile</span><strong>under {s.slo.read_p95_ms} ms</strong><span>{s.worst_read_p95_ms == null ? "No traffic measured yet" : `Slowest read route now: ${s.worst_read_p95_ms} ms`}</span></div>
            <div><span>Availability target</span><strong>{(s.slo.availability * 100).toFixed(1)}%</strong><span>{s.uptime_seconds == null ? "Not measured for the static demo" : `Up for ${Math.round(s.uptime_seconds / 60)} minutes`}</span></div>
            <div><span>Scoring 100k invoice lines</span><strong>under {s.slo.scoring_100k_lines_minutes} min</strong><span>See the load-test report in the repository</span></div>
            <div><span>Version</span><strong>{s.version}</strong><span>sign-in: {s.auth_mode}</span></div>
          </div>
        </section>
      )}
    </>
  );
}
