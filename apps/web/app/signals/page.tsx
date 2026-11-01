"use client";
import { EmptyState, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader eyebrow="Signals" title="Signals" />
      <section className="glass panel">
        <EmptyState image="/img/aur-06-signals.webp" title="Not built yet (P5)" body="Web and social signals arrive in P5." />
      </section>
    </>
  );
}
