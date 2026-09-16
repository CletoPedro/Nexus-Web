import Link from "next/link";

import { cn } from "@/lib/utils";
import type { Task } from "@/types/task";

const PRIORITY_STYLES: Record<Task["priority"], string> = {
  LOW: "bg-muted text-muted-foreground",
  MEDIUM: "bg-muted text-muted-foreground",
  HIGH: "bg-highlight/15 text-highlight",
  CRITICAL: "bg-highlight text-highlight-foreground",
};

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function TaskRow({ task, overdue }: { task: Task; overdue?: boolean }) {
  return (
    <Link
      href="/tasks"
      className={cn(
        "flex items-center gap-2 rounded-[var(--radius-sm)] border px-3 py-2 text-sm hover:bg-muted",
        overdue ? "border-highlight/40" : "border-border",
      )}
    >
      <span className="min-w-0 flex-1 truncate">{task.title}</span>
      <span
        className={cn(
          "shrink-0 rounded-full px-1.5 py-0.5 font-mono text-[10px]",
          PRIORITY_STYLES[task.priority],
        )}
      >
        {task.priority}
      </span>
      {task.due_date && (
        <span
          className={cn(
            "shrink-0 font-mono text-[10px]",
            overdue ? "text-highlight" : "text-muted-foreground",
          )}
        >
          {formatDate(task.due_date)}
        </span>
      )}
    </Link>
  );
}
