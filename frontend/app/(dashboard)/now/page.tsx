"use client";

import { useEffect, useState } from "react";

import { DocumentRow } from "@/components/features/now/document-row";
import { InventoryRow } from "@/components/features/now/inventory-row";
import { MemoryRow } from "@/components/features/now/memory-row";
import { NowSection } from "@/components/features/now/now-section";
import { QuickActions } from "@/components/features/now/quick-actions";
import { TaskRow } from "@/components/features/now/task-row";
import { TimelineRow } from "@/components/features/now/timeline-row";
import { ApiError } from "@/lib/api/client";
import { nowApi } from "@/lib/api/now";
import type { NowSnapshot } from "@/types/now";

export default function NowPage() {
  const [snapshot, setSnapshot] = useState<NowSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await nowApi.get();
      setSnapshot(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load your NEXUS.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, []);

  const todayTasks = snapshot
    ? [...snapshot.overdue_tasks, ...snapshot.high_priority_tasks, ...snapshot.upcoming_tasks]
    : [];

  return (
    <div className="max-w-2xl">
      <h1 className="mb-1 font-display text-3xl italic">Now</h1>
      <p className="mb-6 text-sm text-muted-foreground">What&apos;s happening now.</p>

      {loading && <p className="text-sm text-muted-foreground">Loading your NEXUS…</p>}

      {!loading && error && (
        <p className="mb-4 rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
          {error}
        </p>
      )}

      {!loading && !error && snapshot && (
        <div className="flex flex-col gap-8">
          <section>
            <h2 className="mb-2 font-mono text-xs uppercase tracking-wide text-muted-foreground">
              Quick actions
            </h2>
            <QuickActions onCreated={load} />
          </section>

          <NowSection
            title="Today"
            viewAllHref="/tasks"
            isEmpty={todayTasks.length === 0}
            emptyText="Nothing pending. You're caught up."
          >
            {snapshot.overdue_tasks.map((t) => (
              <TaskRow key={t.id} task={t} overdue />
            ))}
            {snapshot.high_priority_tasks.map((t) => (
              <TaskRow key={t.id} task={t} />
            ))}
            {snapshot.upcoming_tasks.map((t) => (
              <TaskRow key={t.id} task={t} />
            ))}
          </NowSection>

          <NowSection
            title="Recent memory"
            viewAllHref="/memory"
            isEmpty={snapshot.recent_memories.length === 0}
            emptyText="No memories yet."
          >
            {snapshot.recent_memories.map((m) => (
              <MemoryRow key={m.id} memory={m} />
            ))}
          </NowSection>

          <NowSection
            title="Recent documents"
            viewAllHref="/documents"
            isEmpty={snapshot.recent_documents.length === 0}
            emptyText="No documents yet."
          >
            {snapshot.recent_documents.map((d) => (
              <DocumentRow key={d.id} document={d} />
            ))}
          </NowSection>

          <NowSection
            title="Inventory"
            viewAllHref="/inventory"
            isEmpty={snapshot.recent_inventory.length === 0}
            emptyText="No items yet."
          >
            {snapshot.recent_inventory.map((i) => (
              <InventoryRow key={i.id} item={i} />
            ))}
          </NowSection>

          <NowSection
            title="Timeline"
            viewAllHref="/timeline"
            isEmpty={snapshot.recent_timeline.length === 0}
            emptyText="Nothing has happened yet."
          >
            {snapshot.recent_timeline.map((e) => (
              <TimelineRow key={e.id} event={e} />
            ))}
          </NowSection>
        </div>
      )}
    </div>
  );
}
