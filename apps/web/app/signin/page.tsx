"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { apiPost, asset, BASE, STATIC, useApi } from "@/lib/api";
import { supabase, SUPABASE_ENABLED } from "@/lib/supabase";

type Health = { auth_mode: "off" | "local" | "supabase" };

export default function SignInPage() {
  return (
    <Suspense>
      <SignIn />
    </Suspense>
  );
}

function SignIn() {
  const params = useSearchParams();
  const invite = params.get("invite");
  const next = params.get("next");
  const health = useApi<Health>(STATIC ? null : "/api/health");
  const [mode, setMode] = useState<"signin" | "signup">(invite ? "signup" : "signin");
  const [form, setForm] = useState({ email: "", password: "", name: "", workspace: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const set = (key: string, value: string) => setForm((f) => ({ ...f, [key]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (authMode === "supabase") {
        const sb = supabase();
        if (!sb) throw new Error("Supabase is not configured in this build (NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY)");
        const result = mode === "signin"
          ? await sb.auth.signInWithPassword({ email: form.email, password: form.password })
          : await sb.auth.signUp({ email: form.email, password: form.password, options: { data: { name: form.name } } });
        if (result.error) throw new Error(result.error.message);
        if (mode === "signup" && !result.data.session) {
          setError("Check your email to confirm the account, then sign in.");
          return;
        }
        if (invite) await apiPost("/api/auth/accept-invite", { token: invite });
      } else if (mode === "signin") await apiPost("/api/auth/signin", { email: form.email, password: form.password });
      else await apiPost("/api/auth/signup", { ...form, invite });
      const target = next && next.startsWith("/") && !next.startsWith("//") ? next : `${BASE}/queue/`;
      window.location.assign(target);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const authMode = health.data?.auth_mode;
  return (
    <section className="glass split" style={{ padding: 22, maxWidth: 1000, margin: "0 auto", width: "100%" }}>
      <div>
        <img className="only-dark art" src={asset("/img/aur-13-auth.webp")} alt="" />
        <img className="only-light art" src={asset("/img/aur-13-auth-light.webp")} alt="" />
      </div>
      <div className="grid" style={{ gap: 14, alignContent: "center" }}>
        <p className="eyebrow">{invite ? "You have been invited" : "Welcome back"}</p>
        <h1 style={{ fontSize: 32 }}>{mode === "signin" ? "Sign in to your workspace" : "Create your account"}</h1>
        {STATIC && <p className="notice">The public demo has no accounts. <Link href="/overview">Open the demo</Link> to look around, or run RetentionLens with sign-in turned on.</p>}
        {authMode === "off" && <p className="notice">Sign-in is turned off on this local server, so you are using the single local workspace. <Link href="/queue">Open the app</Link>.</p>}
        {authMode === "supabase" && !SUPABASE_ENABLED && <p className="notice">This server uses Supabase Auth, but this web build has no Supabase settings. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY and rebuild.</p>}
        {health.error && <p className="toast error" role="alert">Couldn&apos;t reach the API: {health.error}</p>}
        {(authMode === "local" || (authMode === "supabase" && SUPABASE_ENABLED)) && (
          <>
            <div className="segmented glass" role="tablist" aria-label="Account">
              <button type="button" role="tab" aria-selected={mode === "signin"} aria-pressed={mode === "signin"} onClick={() => setMode("signin")}>Sign in</button>
              <button type="button" role="tab" aria-selected={mode === "signup"} aria-pressed={mode === "signup"} onClick={() => setMode("signup")}>Create account</button>
            </div>
            <form className="grid" style={{ gap: 12 }} onSubmit={submit}>
              {mode === "signup" && (
                <label className="field">Your name
                  <input required autoComplete="name" value={form.name} onChange={(e) => set("name", e.target.value)} />
                </label>
              )}
              <label className="field">Work email
                <input type="email" required autoComplete="email" value={form.email} onChange={(e) => set("email", e.target.value)} />
              </label>
              <label className="field">Password{mode === "signup" && " (at least 12 characters)"}
                <input type="password" required minLength={mode === "signup" ? 12 : 1} autoComplete={mode === "signin" ? "current-password" : "new-password"} value={form.password} onChange={(e) => set("password", e.target.value)} />
              </label>
              {mode === "signup" && !invite && (
                <label className="field">Company or workspace name
                  <input autoComplete="organization" value={form.workspace} onChange={(e) => set("workspace", e.target.value)} />
                </label>
              )}
              {error && <p className="toast error" role="alert">{error}</p>}
              <div><button className="btn primary" type="submit" disabled={busy}>{busy ? "Please wait…" : mode === "signin" ? "Sign in" : invite ? "Join the workspace" : "Create workspace"}</button></div>
              <p className="provenance"><span>Sessions last 7 days in an HttpOnly cookie. Passwords are stored as scrypt hashes.</span></p>
            </form>
          </>
        )}
      </div>
    </section>
  );
}
