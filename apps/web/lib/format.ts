/**
 * Number and date formatting. The data is in pounds sterling whatever the locale; the locale only
 * changes separators, digits and date order. en-GB is the default; en-AE and ar-AE are for UAE users.
 */
export const LOCALES = [
  { value: "en-GB", label: "English (UK)" },
  { value: "en-AE", label: "English (UAE)" },
  { value: "ar-AE", label: "العربية (layout check)" },
] as const;
export type Locale = (typeof LOCALES)[number]["value"];

export function getLocale(): Locale {
  try {
    const saved = typeof window !== "undefined" ? window.localStorage.getItem("rl-locale") : null;
    return (LOCALES.find((l) => l.value === saved)?.value ?? "en-GB") as Locale;
  } catch {
    return "en-GB";
  }
}

const cache = new Map<string, Intl.NumberFormat>();
function nf(kind: string, options: Intl.NumberFormatOptions) {
  // Latin digits keep tables scannable next to English labels, also in the Arabic layout check.
  const locale = getLocale();
  const key = `${locale}|${kind}`;
  if (!cache.has(key)) cache.set(key, new Intl.NumberFormat(`${locale}-u-nu-latn`, options));
  return cache.get(key)!;
}

export const money = (n: number | null | undefined) => (n == null ? "—" : nf("gbp", { style: "currency", currency: "GBP", maximumFractionDigits: 0 }).format(n));
export const moneyShort = (n: number | null | undefined) =>
  n == null ? "—" : nf("gbpc", { style: "currency", currency: "GBP", notation: "compact", maximumFractionDigits: 1 }).format(n);
export const count = (n: number | null | undefined) => (n == null ? "—" : nf("int", { maximumFractionDigits: 0 }).format(n));
export const pct = (n: number | null | undefined, digits = 0) => (n == null ? "—" : `${(n * 100).toFixed(digits)}%`);
export const fixed = (n: number | null | undefined, digits = 3) => (n == null ? "—" : n.toFixed(digits));
export const date = (iso: string | null | undefined) =>
  iso ? new Intl.DateTimeFormat(`${getLocale()}-u-nu-latn`, { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(iso)) : "—";
export const bytes = (n: number) => (n < 1024 * 1024 ? `${Math.max(1, Math.round(n / 1024))} KB` : `${(n / 1024 / 1024).toFixed(1)} MB`);
export const bandLabel = { high: "High risk", watch: "Watch", healthy: "Healthy" } as const;
export const shortHash = (h: string) => h.slice(0, 12) + "…";
