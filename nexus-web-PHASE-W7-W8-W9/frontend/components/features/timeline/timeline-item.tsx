import { Archive, BrainCircuit, CheckSquare, FileText } from "lucide-react";

import type { TimelineEvent, TimelineEventType } from "@/types/timeline";

const EVENT_META: Record<
  TimelineEventType,
  { label: string; icon: typeof BrainCircuit }
> = {
  MEMORY_CREATED: { label: "Memory created", icon: BrainCircuit },
  TASK_CREATED: { label: "Task created", icon: CheckSquare },
  TASK_COMPLETED: { label: "Task completed", icon: CheckSquare },
  DOCUMENT_CREATED: { label: "Document added", icon: FileText },
  INVENTORY_CREATED: { label: "Item added", icon: Archive },
  INVENTORY_UPDATED: { label: "Item updated", icon: Archive },
};

function formatDateTime(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function TimelineItem({ event }: { event: TimelineEvent }) {
  const meta = EVENT_META[event.event_type];
  const Icon = meta.icon;

  return (
    <div className="flex gap-3 rounded-[var(--radius-md)] border border-border bg-card p-4">
      <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <Icon className="size-4" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
          {meta.label}
        </p>
        <p className="mt-0.5 text-sm leading-relaxed truncate">{event.title}</p>
        <p className="mt-1 font-mono text-[11px] text-muted-foreground">
          {formatDateTime(event.occurred_at)}
        </p>
      </div>
    </div>
  );
}
