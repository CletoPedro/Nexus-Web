"use client";

import { Archive, BrainCircuit, CheckSquare, FileText } from "lucide-react";

import { cn } from "@/lib/utils";
import type { SearchResponse, SearchResult, SearchResultType } from "@/types/search";

const GROUP_META: Record<
  SearchResultType,
  { label: string; icon: typeof BrainCircuit }
> = {
  memory: { label: "Memory", icon: BrainCircuit },
  task: { label: "Tasks", icon: CheckSquare },
  document: { label: "Documents", icon: FileText },
  inventory: { label: "Inventory", icon: Archive },
};

const GROUP_ORDER: { key: keyof SearchResponse; type: SearchResultType }[] = [
  { key: "memory", type: "memory" },
  { key: "tasks", type: "task" },
  { key: "documents", type: "document" },
  { key: "inventory", type: "inventory" },
];

export function SearchResultsList({
  results,
  onSelect,
  showRelevance = false,
}: {
  results: SearchResponse;
  onSelect: (result: SearchResult) => void;
  showRelevance?: boolean;
}) {
  if (results.total === 0) {
    return (
      <p className="px-2 py-6 text-center text-sm text-muted-foreground">
        No results found
      </p>
    );
  }

  return (
    <>
      {GROUP_ORDER.map(({ key, type }) => {
        const items = results[key] as SearchResult[];
        if (items.length === 0) return null;
        const meta = GROUP_META[type];
        const Icon = meta.icon;

        return (
          <div key={key} className="mb-2 last:mb-0">
            <p className="px-2 py-1 font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
              {meta.label}
            </p>
            {items.map((result) => (
              <button
                key={result.id}
                type="button"
                onClick={() => onSelect(result)}
                className={cn(
                  "flex w-full items-start gap-2 rounded-[var(--radius-sm)] px-2 py-2 text-left text-sm hover:bg-muted",
                )}
              >
                <Icon className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                <span className="min-w-0 flex-1">
                  <span className="block truncate font-medium">{result.title}</span>
                  {result.content && (
                    <span className="block truncate text-xs text-muted-foreground">
                      {result.content}
                    </span>
                  )}
                </span>
                {showRelevance && (
                  <span className="shrink-0 font-mono text-[10px] text-muted-foreground">
                    {result.relevance.toFixed(2)}
                  </span>
                )}
              </button>
            ))}
          </div>
        );
      })}
    </>
  );
}
