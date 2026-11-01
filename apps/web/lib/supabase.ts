"use client";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Supabase Auth for hosted deployments (API with RL_AUTH_MODE=supabase). Enabled only when both
 * NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are set at build time; the anon key is public by design.
 */
const URL_ = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
export const SUPABASE_ENABLED = Boolean(URL_ && KEY);

let client: SupabaseClient | null = null;
export function supabase(): SupabaseClient | null {
  if (!SUPABASE_ENABLED) return null;
  client ??= createClient(URL_, KEY, { auth: { persistSession: true, autoRefreshToken: true } });
  return client;
}

/** The current access token, for the API's Authorization header; null when signed out or not configured. */
export async function supabaseToken(): Promise<string | null> {
  const sb = supabase();
  if (!sb) return null;
  const { data } = await sb.auth.getSession();
  return data.session?.access_token ?? null;
}
