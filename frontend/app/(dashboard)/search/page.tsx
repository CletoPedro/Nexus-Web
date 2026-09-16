"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { SearchResultsList } from "@/components/features/search/search-results-list";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import { globalSearchApi } from "@/lib/api/search";
import type { SearchResponse, SearchResult } from "@/types/search";

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
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
        const data = await globalSearchApi.search(trimmed, 50);
        setResults(data);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Search failed. Try again.");
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => window.clearTimeout(handle);
  }, [query]);

  function handleSelect(result: SearchResult) {
    router.push(result.target_url);
  }

  const hasQuery = query.trim().length > 0;

  return (
    <div className="max-w-2xl">
      <h1 className="mb-6 font-display text-3xl italic">Search</h1>

      <div className="relative mb-6">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          autoFocus
          placeholder="Search your NEXUS"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      {!hasQuery && (
        <p className="text-sm text-muted-foreground">Search your NEXUS</p>
      )}

      {hasQuery && loading && (
        <p className="text-sm text-muted-foreground">Searching…</p>
      )}

      {hasQuery && !loading && error && (
        <p className="rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
          {error}
        </p>
      )}

      {hasQuery && !loading && !error && results && (
        <SearchResultsList results={results} onSelect={handleSelect} showRelevance />
      )}
    </div>
  );
}
