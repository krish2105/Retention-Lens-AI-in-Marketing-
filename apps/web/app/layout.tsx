import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'RetentionLens | Research Starter', description: '90-day repeat-purchase and customer value forecasting with human-led account reviews' };
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>) {return <html lang="en" suppressHydrationWarning><body>{children}</body></html>;}
