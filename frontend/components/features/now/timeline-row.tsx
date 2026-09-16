import { Archive, BrainCircuit, CheckSquare, FileText } from "lucide-react";
import Link from "next/link";

import type { TimelineEvent, TimelineEventType } from "@/types/timeline";

const EVENT_META: Record<
  TimelineEventType,
  { label: string; icon: typeof BrainCircuit; href: string }
> = {
  MEMORY_CREATED: { label: "Memory created", icon: BrainCircuit, href: "/memory" },
  TASK_CREATED: { label: "Task created", icon: CheckSquare, href: "/tasks" },
  TASK_COMPLETED: { label: "Task completed", icon: CheckSquare, href: "/tasks" },
  DOCUMENT_CREATED: { label: "Document added", icon: FileText, href: "/documents" },
  INVENTORY_CREATED: { label: "Item added", icon: Archive, href: "/inventory" },
  INVENTORY_UPDATED: { label: "Item updated", icon: Archive, href: "/inventory" },
};

export function TimelineRow({ event }: { event: TimelineEvent }) {
  const meta = EVENT_META[event.event_type];
  const Icon = meta.icon;

  return (
    <Link
      href={meta.href}
      className="flex items-center gap-2 rounded-[var(--radius-sm)] border border-border px-3 py-2 text-sm hover:bg-muted"
    >
      <Icon className="size-3.5 shrink-0 text-muted-foreground" />
      <span className="min-w-0 flex-1 truncate">{event.title}</span>
      <span className="shrink-0 font-mono text-[10px] text-muted-foreground">
        {meta.label}
      </span>
    </Link>
  );
}
