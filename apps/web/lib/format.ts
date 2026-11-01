const gbp = new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP", maximumFractionDigits: 0 });
const gbpCompact = new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP", notation: "compact", maximumFractionDigits: 1 });
const int = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });

export const money = (n: number | null | undefined) => (n == null ? "—" : gbp.format(n));
export const moneyShort = (n: number | null | undefined) => (n == null ? "—" : gbpCompact.format(n));
export const count = (n: number | null | undefined) => (n == null ? "—" : int.format(n));
export const pct = (n: number | null | undefined, digits = 0) => (n == null ? "—" : `${(n * 100).toFixed(digits)}%`);
export const fixed = (n: number | null | undefined, digits = 3) => (n == null ? "—" : n.toFixed(digits));
export const bandLabel = { high: "High risk", watch: "Watch", healthy: "Healthy" } as const;
export const shortHash = (h: string) => h.slice(0, 12) + "…";
