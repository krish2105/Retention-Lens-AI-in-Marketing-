"use client";
import Link from "next/link";
import { useState } from "react";
import { apiGet, apiPost, asset, BASE, type Me, useApi } from "@/lib/api";
import { PageHeader } from "@/components/ui";

const STORED = [
  ["Invoice files you upload", "Kept in this workspace's folder until you delete the upload or the workspace"],
  ["Scores and segments", "Recomputed on each upload; deleted with the upload"],
  ["Decisions, drafts and approvals", "Kept as your audit trail until you delete the workspace"],
  ["Member names and emails", "Needed for sign-in and the audit log"],
  ["Prompts to the AI model", "Built from structured account facts only; run on the server, not sent to a third-party AI service"],
];

export default function PrivacyCentre() {
  const me = useApi<Me>("/api/auth/me");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState<{ kind: "ok" | "error"; text: string } | null>(null);
  const owner = me.data?.role === "owner";
  const exportData = async () => {
    try {
      const data = await apiGet("/api/org/export");
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `retentionlens-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setMessage({ kind: "ok", text: "Export downloaded." });
    } catch (e) {
      setMessage({ kind: "error", text: (e as Error).message });
    }
  };
  const erase = async () => {
    try {
      await apiPost("/api/org/delete", { confirm });
      window.location.assign(me.data?.auth_mode === "off" ? `${BASE}/upload/` : `${BASE}/`);
    } catch (e) {
      setMessage({ kind: "error", text: (e as Error).message });
    }
  };
  return (
    <>
      <PageHeader eyebrow="Workspace" title="Privacy and your data." lede="What is stored, for how long, and the controls to take it with you or erase it. Written for UK GDPR and the UAE PDPL; see the full privacy notice." />
      <section className="glass split" style={{ padding: 22 }}>
        <img src={asset("/img/aur-22-privacy.webp")} alt="" />
        <div className="grid" style={{ gap: 10 }}>
          <h2>What this workspace stores</h2>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Stored data">
            <table><tbody>{STORED.map(([what, why]) => <tr key={what}><td><strong>{what}</strong></td><td style={{ color: "var(--muted)" }}>{why}</td></tr>)}</tbody></table>
          </div>
          <p className="provenance"><span><Link href="/legal/privacy">Read the privacy notice</Link></span></p>
        </div>
      </section>
      {message && <p className={`toast ${message.kind}`} role={message.kind === "error" ? "alert" : "status"}>{message.text}</p>}
      <section className="glass panel">
        <h2>Export everything</h2>
        <p style={{ color: "var(--muted)" }}>Download every decision, draft, upload record, outcome and audit event in this workspace as one JSON file.</p>
        <div><button className="btn" type="button" onClick={exportData} disabled={!owner}>Download my data</button></div>
        {!owner && <p className="provenance"><span>Only workspace owners can export or delete.</span></p>}
      </section>
      <section className="glass panel danger" style={{ borderColor: "var(--magenta)" }}>
        <h2>Delete this workspace</h2>
        <p style={{ color: "var(--muted)" }}>Erases uploads, scores, decisions, drafts, outcomes, invites and members&apos; access. It cannot be undone. A record that a deletion happened is kept, with no personal data in it.</p>
        <label className="field" style={{ maxWidth: 420 }}>Type the workspace name <strong style={{ color: "var(--ink)" }}>{me.data?.org.name}</strong> to confirm
          <input value={confirm} onChange={(e) => setConfirm(e.target.value)} disabled={!owner} />
        </label>
        <div><button className="btn danger" type="button" onClick={erase} disabled={!owner || confirm !== me.data?.org.name}>Delete the workspace</button></div>
      </section>
    </>
  );
}
