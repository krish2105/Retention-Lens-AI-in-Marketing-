"use client";
import { EmptyState, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader eyebrow="Product lab" title="Product lab" />
      <section className="glass panel">
        <EmptyState image="/img/aur-05-model-lab.webp" title="Not built yet (P7)" body="Basket and pricing analysis arrives in P7." />
      </section>
    </>
  );
}
