"use client";

import { Check, Pencil, RotateCcw, Trash2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Task, TaskStatus } from "@/types/task";

const PRIORITY_STYLES: Record<Task["priority"], string> = {
  LOW: "bg-muted text-muted-foreground",
  MEDIUM: "bg-muted text-muted-foreground",
  HIGH: "bg-highlight/15 text-highlight",
  CRITICAL: "bg-highlight text-highlight-foreground",
};

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function isOverdue(task: Task): boolean {
  if (!task.due_date) return false;
  if (task.status === "DONE" || task.status === "CANCELLED") return false;
  return new Date(task.due_date).getTime() < Date.now();
}

export function TaskCard({
  task,
  onEdit,
  onDelete,
  onSetStatus,
}: {
  task: Task;
  onEdit: () => void;
  onDelete: () => void;
  onSetStatus: (status: TaskStatus) => void;
}) {
  const done = task.status === "DONE";
  const cancelled = task.status === "CANCELLED";
  const overdue = isOverdue(task);

  return (
    <div
      className={cn(
        "group rounded-[var(--radius-md)] border bg-card p-4 transition-colors",
        overdue ? "border-highlight/50" : "border-border hover:border-accent/50",
      )}
    >
      <div className="flex items-start gap-3">
        <button
          type="button"
          aria-label={done ? "Mark as not done" : "Mark as done"}
          onClick={() => onSetStatus(done ? "TODO" : "DONE")}
          disabled={cancelled}
          className={cn(
            "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border transition-colors",
            done
              ? "border-accent bg-accent text-accent-foreground"
              : "border-border text-transparent hover:border-accent",
            cancelled && "opacity-40",
          )}
        >
          <Check className="size-3.5" />
        </button>

        <div className="min-w-0 flex-1">
          <p
            className={cn(
              "text-sm leading-relaxed",
              (done || cancelled) && "text-muted-foreground line-through",
            )}
          >
            {task.title}
          </p>
          {task.description && (
            <p className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">
              {task.description}
            </p>
          )}
        </div>

        <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
          {!done && !cancelled && (
            <Button
              variant="ghost"
              size="icon"
              aria-label="Cancel task"
              onClick={() => onSetStatus("CANCELLED")}
            >
              <X />
            </Button>
          )}
          {(done || cancelled) && (
            <Button
              variant="ghost"
              size="icon"
              aria-label="Reopen task"
              onClick={() => onSetStatus("TODO")}
            >
              <RotateCcw />
            </Button>
          )}
          <Button variant="ghost" size="icon" aria-label="Edit task" onClick={onEdit}>
            <Pencil />
          </Button>
          <Button variant="ghost" size="icon" aria-label="Delete task" onClick={onDelete}>
            <Trash2 />
          </Button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 pl-8">
        <span
          className={cn(
            "rounded-full px-2 py-0.5 font-mono text-[11px]",
            PRIORITY_STYLES[task.priority],
          )}
        >
          {task.priority}
        </span>
        {task.status === "IN_PROGRESS" && (
          <span className="rounded-full bg-accent/15 px-2 py-0.5 font-mono text-[11px] text-accent">
            IN PROGRESS
          </span>
        )}
        {task.due_date && (
          <span
            className={cn(
              "font-mono text-[11px]",
              overdue ? "text-highlight" : "text-muted-foreground",
            )}
          >
            {overdue ? "Overdue: " : "Due "}
            {formatDate(task.due_date)}
          </span>
        )}
      </div>
    </div>
  );
}
