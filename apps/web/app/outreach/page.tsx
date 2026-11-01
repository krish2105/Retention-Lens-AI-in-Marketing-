"use client";
import { EmptyState, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader eyebrow="Outreach studio" title="Outreach studio" />
      <section className="glass panel">
        <EmptyState image="/img/aur-04-outreach.webp" title="Not built yet (P6)" body="The AI outreach studio arrives in P6." />
      </section>
    </>
  );
}
