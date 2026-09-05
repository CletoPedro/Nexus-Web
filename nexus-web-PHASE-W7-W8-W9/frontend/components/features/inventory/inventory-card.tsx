"use client";

import { LinkIcon, Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { InventoryItem } from "@/types/inventory";

export function InventoryCard({
  item,
  linkedDocumentTitle,
  onEdit,
  onDelete,
}: {
  item: InventoryItem;
  linkedDocumentTitle?: string;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="group rounded-[var(--radius-md)] border border-border bg-card p-4 transition-colors hover:border-accent/50">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium leading-relaxed">
            {item.name}
            {item.quantity > 1 && (
              <span className="ml-2 font-mono text-xs text-muted-foreground">
                ×{item.quantity}
              </span>
            )}
          </p>
          {item.description && (
            <p className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">
              {item.description}
            </p>
          )}
        </div>
        <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
          <Button variant="ghost" size="icon" aria-label="Edit item" onClick={onEdit}>
            <Pencil />
          </Button>
          <Button variant="ghost" size="icon" aria-label="Delete item" onClick={onDelete}>
            <Trash2 />
          </Button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {item.category && (
          <span className="rounded-full bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
            {item.category}
          </span>
        )}
        {item.location && (
          <span className="rounded-full bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
            {item.location}
          </span>
        )}
        {linkedDocumentTitle && (
          <span className="flex items-center gap-1 rounded-full bg-accent/15 px-2 py-0.5 font-mono text-[11px] text-accent">
            <LinkIcon className="size-3" />
            {linkedDocumentTitle}
          </span>
        )}
      </div>
    </div>
  );
}
