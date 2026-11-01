"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { apiPost, asset, BASE, type Me, STATIC, useApi } from "@/lib/api";
import { getLocale } from "@/lib/format";
import { OnboardingTour } from "./OnboardingTour";
import { Icon, ThemeToggle } from "./ui";

const NAV = [
  { href: "/overview", label: "Overview", icon: "overview" },
  { href: "/queue", label: "This week", icon: "queue" },
  { href: "/accounts", label: "Accounts", icon: "accounts" },
  { href: "/segments", label: "Segments", icon: "segments" },
  { href: "/signals", label: "Signals", icon: "signals" },
  { href: "/outreach", label: "Outreach studio", icon: "outreach" },
  { href: "/product-lab", label: "Product lab", icon: "product" },
  { href: "/model-lab", label: "Model lab", icon: "lab" },
  { href: "/data", label: "Data", icon: "data" },
  { href: "/upload", label: "Upload data", icon: "upload" },
  { href: "/evidence", label: "Course evidence", icon: "evidence" },
];
const WORKSPACE = [
  { href: "/team", label: "Team", icon: "team" },
  { href: "/privacy", label: "Privacy & data", icon: "shield" },
  { href: "/billing", label: "Plan & billing", icon: "card" },
  { href: "/settings", label: "Settings", icon: "settings" },
];
/** Marketing and account pages: no sidebar, no sign-in needed. */
const PUBLIC = ["/", "/pricing", "/signin", "/status", "/legal/privacy", "/legal/terms", "/case-study"];

const norm = (path: string) => (path.length > 1 ? path.replace(/\/$/, "") : path);

export function Shell({ children }: { children: ReactNode }) {
  const path = norm(usePathname());
  useEffect(() => {
    const locale = getLocale();
    document.documentElement.lang = locale;
    document.documentElement.dir = locale.startsWith("ar") ? "rtl" : "ltr";
  }, []);
  const aurora = (
    <div className="aurora" aria-hidden="true">
      <span />
      <span />
      <span />
    </div>
  );
  if (PUBLIC.includes(path)) {
    return (
      <>
        {aurora}
        <a href="#main" className="sr-only">Skip to content</a>
        <SiteHeader path={path} />
        <main className="site" id="main">{children}</main>
        <SiteFooter />
      </>
    );
  }
  return <AppShell path={path} aurora={aurora}>{children}</AppShell>;
}

function AppShell({ path, aurora, children }: { path: string; aurora: ReactNode; children: ReactNode }) {
  const me = useApi<Me>("/api/auth/me");
  const signOut = async () => {
    await apiPost("/api/auth/signout", {}).catch(() => undefined);
    window.location.assign(`${BASE}/signin/`);
  };
  return (
    <>
      {aurora}
      <a href="#main" className="sr-only">Skip to content</a>
      <div className="shell">
        <aside className="sidebar glass">
          <Link href="/overview" className="brand">
            <img src={asset("/img/aur-08-mark.webp")} alt="" />
            <span>
              <strong>RetentionLens</strong>
              <small>{me.data ? me.data.org.name : "MAIB AI 208"}</small>
            </span>
          </Link>
          <nav className="nav" aria-label="Main">
            {NAV.map((item) => (
              <Link key={item.href} href={item.href} data-tour={item.href.slice(1)} aria-current={path === item.href ? "page" : undefined}>
                <Icon name={item.icon} />
                {item.label}
              </Link>
            ))}
            <span className="nav-group" aria-hidden="true">Workspace</span>
            {WORKSPACE.map((item) => (
              <Link key={item.href} href={item.href} aria-current={path === item.href ? "page" : undefined}>
                <Icon name={item.icon} />
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="side-foot">
            {me.data && me.data.auth_mode !== "off" ? (
              <>
                <strong>{me.data.user.name}</strong>
                <span>{me.data.user.email} · {me.data.role}</span>
                <button type="button" className="btn" onClick={signOut}>Sign out</button>
              </>
            ) : (
              <>
                <strong>{me.data?.org.active_dataset ? "Your uploaded data" : "UCI Online Retail II"}</strong>
                <span>{me.data?.org.active_dataset ? "Scored in this workspace" : "1,067,371 invoice lines · CC BY 4.0"}</span>
              </>
            )}
            <span>Decision support only. Nothing is sent without your approval.</span>
          </div>
        </aside>
        <div className="main" id="main">
          <div style={{ display: "flex", justifyContent: STATIC ? "space-between" : "flex-end", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            {STATIC && (
              <p className="demo-banner">
                <strong>Public demo</strong> · read-only snapshot scored 2011-12-10 · <a href="https://github.com/krish2105/Retention-Lens-AI-in-Marketing-">run it locally</a> for uploads, AI drafting and decisions
              </p>
            )}
            <ThemeToggle />
          </div>
          {children}
        </div>
      </div>
      <OnboardingTour />
    </>
  );
}

function SiteHeader({ path }: { path: string }) {
  return (
    <header className="site-header glass">
      <Link href="/" className="brand">
        <img src={asset("/img/aur-08-mark.webp")} alt="" />
        <span><strong>RetentionLens</strong></span>
      </Link>
      <nav className="site-nav" aria-label="Site">
        <Link href="/#how" aria-current={undefined}>How it works</Link>
        <Link href="/pricing" aria-current={path === "/pricing" ? "page" : undefined}>Pricing</Link>
        <Link href="/case-study" aria-current={path === "/case-study" ? "page" : undefined}>Case study</Link>
        <Link href="/status" aria-current={path === "/status" ? "page" : undefined}>Status</Link>
      </nav>
      <div className="site-actions">
        <ThemeToggle />
        {!STATIC && <Link className="btn" href="/signin">Sign in</Link>}
        <Link className="btn primary" href="/overview">{STATIC ? "Open the demo" : "Open the app"}</Link>
      </div>
    </header>
  );
}

function SiteFooter() {
  return (
    <footer className="site-footer">
      <span>RetentionLens · a MAIB AI 208 project by Krishna Mathur</span>
      <nav aria-label="Legal" className="row" style={{ gap: 14 }}>
        <Link href="/legal/privacy">Privacy notice</Link>
        <Link href="/legal/terms">Terms</Link>
        <Link href="/status">Status</Link>
        <a href="https://github.com/krish2105/Retention-Lens-AI-in-Marketing-">Source on GitHub</a>
      </nav>
      <span>Reference data: UCI Online Retail II, CC BY 4.0. Illustrations are AI-generated.</span>
    </footer>
  );
}
