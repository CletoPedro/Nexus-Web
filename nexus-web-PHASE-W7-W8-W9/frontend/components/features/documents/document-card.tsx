"use client";

import { Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Document } from "@/types/document";

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function isExpired(doc: Document): boolean {
  if (!doc.expiry_date) return false;
  return new Date(doc.expiry_date).getTime() < Date.now();
}

export function DocumentCard({
  document,
  onEdit,
  onDelete,
}: {
  document: Document;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const expired = isExpired(document);

  return (
    <div
      className={cn(
        "group rounded-[var(--radius-md)] border bg-card p-4 transition-colors",
        expired ? "border-highlight/50" : "border-border hover:border-accent/50",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium leading-relaxed">{document.title}</p>
          {document.description && (
            <p className="mt-1 text-sm text-muted-foreground whitespace-pre-wrap">
              {document.description}
            </p>
          )}
          {document.storage_path && (
            <p className="mt-1 font-mono text-[11px] text-muted-foreground truncate">
              {document.storage_path}
            </p>
          )}
        </div>
        <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
          <Button variant="ghost" size="icon" aria-label="Edit document" onClick={onEdit}>
            <Pencil />
          </Button>
          <Button variant="ghost" size="icon" aria-label="Delete document" onClick={onDelete}>
            <Trash2 />
          </Button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {document.category && (
          <span className="rounded-full bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
            {document.category}
          </span>
        )}
        {document.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground"
          >
            {tag}
          </span>
        ))}
        {document.expiry_date && (
          <span
            className={cn(
              "font-mono text-[11px]",
              expired ? "text-highlight" : "text-muted-foreground",
            )}
          >
            {expired ? "Expired: " : "Expires "}
            {formatDate(document.expiry_date)}
          </span>
        )}
      </div>
    </div>
  );
}
