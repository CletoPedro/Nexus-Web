"use client";

import { Search, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { SearchResultsList } from "@/components/features/search/search-results-list";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import { globalSearchApi } from "@/lib/api/search";
import type { SearchResponse, SearchResult } from "@/types/search";

export function GlobalSearchDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Reset dialog state whenever it opens — a fresh search each time,
    // not a continuation of whatever was last typed.
    if (open) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setQuery("");
      setResults(null);
      setError(null);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const trimmed = query.trim();
    if (!trimmed) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setResults(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    const handle = window.setTimeout(async () => {
      try {
        const data = await globalSearchApi.search(trimmed);
        setResults(data);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Search failed. Try again.");
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => window.clearTimeout(handle);
  }, [query, open]);

  useEffect(() => {
    if (!open) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  function handleSelect(result: SearchResult) {
    onClose();
    router.push(result.target_url);
  }

  const hasQuery = query.trim().length > 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-foreground/20 backdrop-blur-[2px] px-4 pt-[10vh]"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="w-full max-w-lg rounded-[var(--radius-lg)] border border-border bg-card shadow-lg"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Search NEXUS"
      >
        <div className="flex items-center gap-2 border-b border-border px-4">
          <Search className="size-4 shrink-0 text-muted-foreground" />
          <Input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your NEXUS"
            className="border-0 px-0 focus-visible:outline-none"
          />
          <button
            type="button"
            aria-label="Close search"
            onClick={onClose}
            className="shrink-0 rounded-[var(--radius-sm)] p-1 text-muted-foreground hover:bg-muted"
          >
            <X className="size-4" />
          </button>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2">
          {!hasQuery && (
            <p className="px-2 py-6 text-center text-sm text-muted-foreground">
              Search your NEXUS
            </p>
          )}

          {hasQuery && loading && (
            <p className="px-2 py-6 text-center text-sm text-muted-foreground">
              Searching…
            </p>
          )}

          {hasQuery && !loading && error && (
            <p className="px-2 py-6 text-center text-sm text-highlight">{error}</p>
          )}

          {hasQuery && !loading && !error && results && (
            <SearchResultsList results={results} onSelect={handleSelect} />
          )}
        </div>
      </div>
    </div>
  );
}
