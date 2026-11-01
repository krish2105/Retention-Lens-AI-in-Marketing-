"use client";
import { API, useApi } from "@/lib/api";
import { ErrorState, PageHeader, ThemeToggle } from "@/components/ui";

type Health = { ok: boolean; serving_ready: boolean; generated_at: string | null; ollama: { available: boolean; model: string } };

export default function SettingsPage() {
  const health = useApi<Health>("/api/health");
  const h = health.data;
  return (
    <>
      <PageHeader eyebrow="Settings" title="Appearance and system status." />
      <section className="glass panel">
        <h2>Appearance</h2>
        <p className="lede" style={{ marginTop: 0 }}>Choose light, dark or follow your system. The choice is saved in this browser. 3D charts and graphs switch with it.</p>
        <div><ThemeToggle /></div>
        <p className="provenance">Respects reduced motion (no animation) and reduced transparency (solid panels, no aurora).</p>
      </section>
      <section className="glass panel">
        <h2>Status</h2>
        {health.error && <ErrorState message={health.error} onRetry={health.reload} />}
        {h && (
          <div className="kv">
            <div><span>API</span><strong>{API}</strong></div>
            <div><span>Model results</span><strong>{h.serving_ready ? `Built ${h.generated_at?.slice(0, 16)}` : "Not built: run cli serve"}</strong></div>
            <div><span>Local AI model</span><strong>{h.ollama.model}</strong></div>
            <div><span>Local AI status</span><strong className={h.ollama.available ? "tone-healthy" : "tone-high"}>{h.ollama.available ? "Running" : "Not running: start Ollama"}</strong></div>
          </div>
        )}
      </section>
      <section className="glass panel">
        <h2>Data and privacy</h2>
        <p>Runs on this computer only. Customer IDs in the dataset are pseudonymous numbers. Decisions, drafts and the audit log are stored in a local SQLite file. There is no sign-in and no multi-tenant isolation, so don&apos;t expose this service to a network or load real customer data into it.</p>
      </section>
    </>
  );
}
