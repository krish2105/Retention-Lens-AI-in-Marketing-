"use client";
import { EmptyState, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader eyebrow="Segments" title="Segments" />
      <section className="glass panel">
        <EmptyState image="/img/aur-02-galaxy.webp" title="Not built yet (P4)" body="Customer galaxy and segments arrive in P4." />
      </section>
    </>
  );
}
