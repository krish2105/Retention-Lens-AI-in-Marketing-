"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { asset, STATIC } from "@/lib/api";
import { Icon, ThemeToggle } from "./ui";

const NAV = [
  { href: "/", label: "Overview", icon: "overview" },
  { href: "/accounts", label: "Accounts", icon: "accounts" },
  { href: "/segments", label: "Segments", icon: "segments" },
  { href: "/signals", label: "Signals", icon: "signals" },
  { href: "/outreach", label: "Outreach studio", icon: "outreach" },
  { href: "/product-lab", label: "Product lab", icon: "product" },
  { href: "/model-lab", label: "Model lab", icon: "lab" },
  { href: "/data", label: "Data", icon: "data" },
  { href: "/evidence", label: "Course evidence", icon: "evidence" },
  { href: "/settings", label: "Settings", icon: "settings" },
];

export function Shell({ children }: { children: ReactNode }) {
  const path = usePathname();
  return (
    <>
      <div className="aurora" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <a href="#main" className="sr-only">
        Skip to content
      </a>
      <div className="shell">
        <aside className="sidebar glass">
          <Link href="/" className="brand">
            <img src={asset("/img/aur-08-mark.webp")} alt="" />
            <span>
              <strong>RetentionLens</strong>
              <small>MAIB AI 208</small>
            </span>
          </Link>
          <nav className="nav" aria-label="Main">
            {NAV.map((item) => (
              <Link key={item.href} href={item.href} aria-current={path === item.href ? "page" : undefined}>
                <Icon name={item.icon} />
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="side-foot">
            <strong>UCI Online Retail II</strong>
            <span>1,067,371 invoice lines · CC BY 4.0</span>
            <span>Decision support only. Nothing is sent without your approval.</span>
          </div>
        </aside>
        <div className="main" id="main">
          <div style={{ display: "flex", justifyContent: STATIC ? "space-between" : "flex-end", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            {STATIC && (
              <p className="demo-banner">
                <strong>Public demo</strong> · read-only snapshot scored 2011-12-10 · <a href="https://github.com/krish2105/Retention-Lens-AI-in-Marketing-">run it locally</a> for AI drafting and decisions
              </p>
            )}
            <ThemeToggle />
          </div>
          {children}
        </div>
      </div>
    </>
  );
}
