"use client";
import { EmptyState, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader eyebrow="Course evidence" title="Course evidence" />
      <section className="glass panel">
        <EmptyState image="/img/aur-03-import.webp" title="Not built yet (P8)" body="The course evidence map arrives in P8." />
      </section>
    </>
  );
}
