import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, Space_Grotesk } from "next/font/google";
import { Shell } from "@/components/Shell";
import { Providers } from "./providers";
import "./globals.css";

const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
const space = Space_Grotesk({ subsets: ["latin", "latin-ext"], variable: "--font-space", display: "swap" });
const plex = IBM_Plex_Mono({ subsets: ["latin", "latin-ext"], weight: ["400", "500"], variable: "--font-plex", display: "swap" });

export const metadata: Metadata = {
  title: "RetentionLens",
  description: "90-day lapse risk and customer value for wholesale accounts, with human-approved outreach.",
  icons: { icon: [{ url: `${base}/icon-192.png`, sizes: "192x192" }, { url: `${base}/icon-512.png`, sizes: "512x512" }], apple: `${base}/apple-touch-icon.png` },
  openGraph: { images: [`${base}/img/aur-10-og.webp`] },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f3f4fb" },
    { media: "(prefers-color-scheme: dark)", color: "#070912" },
  ],
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-GB" suppressHydrationWarning className={`${space.variable} ${plex.variable}`}>
      <body>
        <Providers>
          <Shell>{children}</Shell>
        </Providers>
      </body>
    </html>
  );
}
