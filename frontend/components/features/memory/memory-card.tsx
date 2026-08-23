"use client";

import { Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { Memory } from "@/types/memory";

function formatTimestamp(iso: string | null): string {
  if (!iso) return "";
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function MemoryCard({
  memory,
  onEdit,
  onDelete,
}: {
  memory: Memory;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="group rounded-[var(--radius-md)] border border-border bg-card p-4 transition-colors hover:border-accent/50">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {memory.content}
        </p>
        <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
          <Button variant="ghost" size="icon" aria-label="Edit memory" onClick={onEdit}>
            <Pencil />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Delete memory"
            onClick={onDelete}
          >
            <Trash2 />
          </Button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {memory.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground"
          >
            {tag}
          </span>
        ))}
        {memory.created_at && (
          <span className="ml-auto font-mono text-[11px] text-muted-foreground">
            {formatTimestamp(memory.created_at)}
          </span>
        )}
      </div>
    </div>
  );
}
