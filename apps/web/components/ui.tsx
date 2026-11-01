"use client";
import { useTheme } from "next-themes";
import { useEffect, useState, type ReactNode } from "react";
import { asset, BASE, type Band, type Summary } from "@/lib/api";
import { bandLabel, shortHash } from "@/lib/format";
import { t } from "@/lib/i18n";

const ICONS: Record<string, ReactNode> = {
  sun: <path d="M12 4V2M12 22v-2M4 12H2M22 12h-2M5.6 5.6 4.2 4.2M19.8 19.8l-1.4-1.4M5.6 18.4l-1.4 1.4M19.8 4.2l-1.4 1.4M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z" />,
  moon: <path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" />,
  system: <path d="M3 5h18v11H3zM8 20h8M12 16v4" />,
  overview: <path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" />,
  accounts: <path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21a7 7 0 0 1 14 0M16 3.5a4 4 0 0 1 0 7.5M18 14c2.4.9 4 3.5 4 7" />,
  segments: <path d="M6 7a2 2 0 1 0 0-.01M17 6a2 2 0 1 0 0-.01M12 18a2 2 0 1 0 0-.01M19 16a1.5 1.5 0 1 0 0-.01M5 17a1.5 1.5 0 1 0 0-.01" />,
  signals: <path d="M3 12h4l3-7 4 14 3-7h4" />,
  outreach: <path d="M4 5h16v11H8l-4 4z" />,
  product: <path d="M3 7l9-4 9 4-9 4zM3 7v10l9 4 9-4V7M12 11v10" />,
  lab: <path d="M9 3v6l-5 9a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-5-9V3M8 3h8" />,
  data: <path d="M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3zM4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" />,
  evidence: <path d="M5 3h10l4 4v14H5zM9 12h6M9 16h4" />,
  settings: <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />,
  close: <path d="M6 6l12 12M18 6 6 18" />,
  queue: <path d="M4 6h16M4 12h10M4 18h7M17 15l2 2 4-4" />,
  upload: <path d="M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />,
  team: <path d="M8 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 20a6 6 0 0 1 12 0M16 11a3 3 0 1 0 0-6M17.5 14.5A5.5 5.5 0 0 1 22 20" />,
  shield: <path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6zM9 12l2 2 4-4" />,
  card: <path d="M3 6h18v12H3zM3 10h18M7 15h4" />,
  check: <path d="M5 12l5 5L20 7" />,
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
};

export function Icon({ name }: { name: keyof typeof ICONS | string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {ICONS[name]}
    </svg>
  );
}

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [animate, setAnimate] = useState(false);
  useEffect(() => {
    setMounted(true);
    // Place the thumb first, then allow it to slide, so it does not glide in from "Light" on every page load.
    const id = window.requestAnimationFrame(() => window.requestAnimationFrame(() => setAnimate(true)));
    return () => window.cancelAnimationFrame(id);
  }, []);
  const options = [
    { value: "light", label: "Light", icon: "sun" },
    { value: "dark", label: "Dark", icon: "moon" },
    { value: "system", label: "System", icon: "system" },
  ];
  // Server render does not know the saved theme; place the thumb only after mount to avoid a hydration mismatch.
  const active = mounted ? Math.max(0, options.findIndex((o) => o.value === theme)) : 0;
  const choose = (next: string, event: React.MouseEvent<HTMLButtonElement>) => {
    if (next === theme) return;
    const root = document.documentElement;
    const doc = document as Document & { startViewTransition?: (cb: () => void) => { finished: Promise<void> } };
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // Reveal grows from the centre of the chosen button, so keyboard use looks the same as a click.
    const box = event.currentTarget.getBoundingClientRect();
    root.style.setProperty("--vt-x", `${box.left + box.width / 2}px`);
    root.style.setProperty("--vt-y", `${box.top + box.height / 2}px`);
    if (!doc.startViewTransition || reduce) {
      setTheme(next);
      return;
    }
    root.classList.add("theme-switching");
    doc.startViewTransition(() => setTheme(next)).finished.finally(() => root.classList.remove("theme-switching"));
  };
  return (
    <div className="segmented glass theme-toggle" role="group" aria-label="Colour theme" data-ready={mounted} data-animate={animate}>
      <span className="thumb" aria-hidden="true" style={{ transform: `translateX(${active * 100}%)` }} />
      {options.map((o) => (
        <button key={o.value} type="button" aria-pressed={mounted ? theme === o.value : false} aria-label={`${o.label} theme`} onClick={(e) => choose(o.value, e)}>
          <Icon name={o.icon} />
          <span className="label">{t(o.label)}</span>
        </button>
      ))}
    </div>
  );
}

export function RiskPill({ band, p }: { band: Band; p?: number }) {
  return (
    <span className={`pill tone-${band}`}>
      {bandLabel[band]}
      {p != null && <span className="mono">{Math.round(p * 100)}%</span>}
    </span>
  );
}

export function Loading({ rows = 3 }: { rows?: number }) {
  return (
    <div className="grid" aria-busy="true" aria-label="Loading">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: 22 }} />
      ))}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const notBuilt = message.includes("cli serve") || message.includes("reference dataset only");
  const noData = message.startsWith("No data yet");
  const apiDown = /fetch|network|load failed/i.test(message);
  if (noData) {
    return (
      <div className="state">
        <img src={asset("/img/aur-14-welcome.webp")} alt="" />
        <strong>This workspace has no data yet</strong>
        <span>Upload a CSV or Excel export of your invoices, or load the sample dataset to look around first.</span>
        <a className="btn primary" href={`${BASE}/upload/`}>Upload invoices</a>
      </div>
    );
  }
  return (
    <div className="state" role="alert">
      <img src={asset("/img/aur-07-offline.webp")} alt="" />
      <strong>{notBuilt ? "Not available for this data" : apiDown ? "Couldn't reach the RetentionLens API" : "Something went wrong"}</strong>
      <span>{notBuilt || !apiDown ? message : `Start it with: cd services/api && .venv/bin/uvicorn app.main:app --port 8000 (${message})`}</span>
      {onRetry && (
        <button className="btn" type="button" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ image, title, body, action }: { image: string; title: string; body: string; action?: ReactNode }) {
  return (
    <div className="state">
      <img src={asset(image)} alt="" />
      <strong>{title}</strong>
      <span>{body}</span>
      {action}
    </div>
  );
}

export function Provenance({ summary, extra }: { summary?: Summary | null; extra?: string }) {
  if (!summary) return null;
  return (
    <p className="provenance">
      <span>Source: {summary.evaluation_run ? `UCI Online Retail II (${summary.licence})` : summary.data_source}</span>
      <span>data sha256 {shortHash(summary.data_sha256)}</span>
      <span>scored at {summary.scoring_cutoff}</span>
      <span>model {summary.model}</span>
      {summary.evaluation_run && <span>eval run {summary.evaluation_run}</span>}
      {extra && <span>{extra}</span>}
    </p>
  );
}

export function PageHeader({ eyebrow, title, lede, children }: { eyebrow: string; title: string; lede?: string; children?: ReactNode }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {lede && <p className="lede">{lede}</p>}
      </div>
      {children}
    </header>
  );
}
