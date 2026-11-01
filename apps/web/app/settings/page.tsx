"use client";
import { useEffect, useState } from "react";
import { API, STATIC, useApi } from "@/lib/api";
import { getLocale, LOCALES, type Locale, money } from "@/lib/format";
import { resetTour } from "@/components/OnboardingTour";
import { ErrorState, PageHeader, ThemeToggle } from "@/components/ui";

type Health = { ok: boolean; version?: string; auth_mode?: string; serving_ready: boolean; generated_at: string | null; ollama: { available: boolean; model: string } };

export default function SettingsPage() {
  const health = useApi<Health>("/api/health");
  const h = health.data;
  const [locale, setLocale] = useState<Locale>("en-GB");
  const [toured, setToured] = useState(false);
  useEffect(() => setLocale(getLocale()), []);
  const chooseLocale = (value: Locale) => {
    try {
      window.localStorage.setItem("rl-locale", value);
    } catch {}
    setLocale(value);
    // Formatters and text direction are read at load, so reload to apply everywhere.
    window.location.reload();
  };
  return (
    <>
      <PageHeader eyebrow="Settings" title="Appearance, region and system status." />
      <section className="glass panel">
        <h2>Appearance</h2>
        <p className="lede" style={{ marginTop: 0 }}>Choose light, dark or follow your system. The choice is saved in this browser. 3D charts and graphs switch with it.</p>
        <div><ThemeToggle /></div>
        <p className="provenance">Respects reduced motion (no animation) and reduced transparency (solid panels, no aurora).</p>
      </section>
      <section className="glass panel">
        <h2>Region and number format</h2>
        <p className="lede" style={{ marginTop: 0 }}>Changes separators and date order. Amounts stay in the currency of the data (pounds for the reference dataset).</p>
        <label className="field" style={{ maxWidth: 320 }}>Format
          <select value={locale} onChange={(e) => chooseLocale(e.target.value as Locale)}>
            {LOCALES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>
        </label>
        <p className="provenance"><span>Example: {money(1234567)} · {new Date(Date.UTC(2026, 0, 31)).toLocaleDateString(locale, { timeZone: "UTC" })}</span></p>
        {locale.startsWith("ar") && <p className="notice">Arabic layout check: the interface switches to right-to-left so layouts can be tested for UAE users. The text itself is not translated yet.</p>}
      </section>
      <section className="glass panel">
        <h2>Tour</h2>
        <div><button className="btn" type="button" onClick={() => { resetTour(); setToured(true); }}>{toured ? "The tour will show on your next page load" : "Show the quick tour again"}</button></div>
      </section>
      {!STATIC && (
        <section className="glass panel">
          <h2>Status</h2>
          {health.error && <ErrorState message={health.error} onRetry={health.reload} />}
          {h && (
            <div className="kv">
              <div><span>API</span><strong>{API}</strong></div>
              <div><span>Version · sign-in</span><strong>{h.version ?? "—"} · {h.auth_mode ?? "off"}</strong></div>
              <div><span>Reference results</span><strong>{h.serving_ready ? `Built ${h.generated_at?.slice(0, 16)}` : "Not built: run cli serve"}</strong></div>
              <div><span>Local AI ({h.ollama.model})</span><strong className={h.ollama.available ? "tone-healthy" : "tone-high"}>{h.ollama.available ? "Running" : "Not running: start Ollama"}</strong></div>
            </div>
          )}
        </section>
      )}
      <section className="glass panel">
        <h2>Data and privacy</h2>
        <p>With sign-in off (the default for local use) there is one local workspace: run it on your own computer only. With RL_AUTH_MODE=local or supabase, every company gets its own workspace, roles, and export and delete controls under Privacy and data.</p>
      </section>
    </>
  );
}
