"use client";
import { useState } from "react";
import { apiPost, asset, type Me, useApi } from "@/lib/api";
import { date } from "@/lib/format";
import { ErrorState, PageHeader } from "@/components/ui";

type Member = { id: string; email: string; name: string; role: string; created_at: string | null };
type Members = { members: Member[]; invites: { email: string; role: string; expires_at: string }[] };

const ROLES = [
  { value: "owner", label: "Owner", body: "Everything, including members, billing, export and deletion" },
  { value: "reviewer", label: "Reviewer", body: "Upload data, record decisions, draft and approve outreach" },
  { value: "viewer", label: "Viewer", body: "Read-only: see accounts, queue and results" },
];

export default function TeamPage() {
  const me = useApi<Me>("/api/auth/me");
  const members = useApi<Members>("/api/org/members");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("reviewer");
  const [link, setLink] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const owner = me.data?.role === "owner";
  const off = me.data?.auth_mode === "off";
  const act = async (fn: () => Promise<unknown>) => {
    setError(null);
    try {
      await fn();
      members.reload();
    } catch (e) {
      setError((e as Error).message);
    }
  };
  return (
    <>
      <PageHeader eyebrow="Workspace" title="Your team." lede="People in this workspace and what each can do. Every decision in the audit log carries the name of the person who made it." />
      <section className="glass split" style={{ padding: 22 }}>
        <img src={asset("/img/aur-21-team.webp")} alt="" />
        <div className="grid" style={{ gap: 10, alignContent: "center" }}>
          {ROLES.map((r) => <p key={r.value}><strong>{r.label}</strong> <span style={{ color: "var(--muted)" }}>· {r.body}</span></p>)}
          {off && <p className="notice">Sign-in is off on this server, so there is one local user. Start the API with RL_AUTH_MODE=local to add people.</p>}
        </div>
      </section>
      <section className="glass panel">
        <h2>Members</h2>
        {members.error && <ErrorState message={members.error} onRetry={members.reload} />}
        {error && <p className="toast error" role="alert">{error}</p>}
        {members.data && (
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Members">
            <table>
              <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th></th></tr></thead>
              <tbody>
                {members.data.members.map((m) => (
                  <tr key={m.id}>
                    <td>{m.name}</td>
                    <td>{m.email}</td>
                    <td>
                      {owner && !off && m.id !== me.data?.user.id ? (
                        <select className="control" aria-label={`Role for ${m.name}`} value={m.role} onChange={(e) => act(() => apiPost(`/api/org/members/${m.id}/role`, { role: e.target.value }))}>
                          {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
                        </select>
                      ) : m.role}
                    </td>
                    <td>{date(m.created_at)}</td>
                    <td>{owner && !off && m.id !== me.data?.user.id && <button className="btn danger" type="button" onClick={() => window.confirm(`Remove ${m.name} from this workspace?`) && act(() => apiPost(`/api/org/members/${m.id}/remove`, {}))}>Remove</button>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {members.data && members.data.invites.length > 0 && <p className="provenance">{members.data.invites.map((i) => <span key={i.email}>Invited {i.email} as {i.role}, expires {date(i.expires_at)}</span>)}</p>}
      </section>
      {owner && !off && (
        <section className="glass panel">
          <h2>Invite someone</h2>
          <form className="toolbar" onSubmit={(e) => { e.preventDefault(); act(async () => { const r = await apiPost<{ invite_url: string }>("/api/org/invites", { email, role }); setLink(r.invite_url); setEmail(""); }); }}>
            <label className="field grow">Their work email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>
            <label className="field">Role<select value={role} onChange={(e) => setRole(e.target.value)}>{ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}</select></label>
            <button className="btn primary" type="submit">Create invite link</button>
          </form>
          {link && (
            <div className="notice">
              <p>Send this link to them yourself. It works once, for that email address only, for 7 days. It will not be shown again.</p>
              <p className="mono" style={{ overflowWrap: "anywhere" }}>{link}</p>
            </div>
          )}
        </section>
      )}
    </>
  );
}
