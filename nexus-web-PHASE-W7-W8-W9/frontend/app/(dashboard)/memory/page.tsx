"use client";

import { Plus, Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MemoryCard } from "@/components/features/memory/memory-card";
import { MemoryForm, type MemoryFormValues } from "@/components/features/memory/memory-form";
import { ApiError } from "@/lib/api/client";
import { memoryApi } from "@/lib/api/memory";
import type { Memory } from "@/types/memory";

type ViewState =
  | { mode: "idle" }
  | { mode: "creating" }
  | { mode: "editing"; memory: Memory };

export default function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewState>({ mode: "idle" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [searchTerm, setSearchTerm] = useState("");
  const [activeSearch, setActiveSearch] = useState<string | null>(null);

  async function loadMemories(search?: string) {
    setLoading(true);
    setError(null);
    try {
      const data = search ? await memoryApi.search(search) : await memoryApi.list();
      setMemories(data);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Data-fetch-on-mount: the recommended effect pattern per React docs,
    // even though the new set-state-in-effect lint rule flags the
    // synchronous setLoading(true) at the top of loadMemories.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadMemories();
  }, []);

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = searchTerm.trim();
    if (!trimmed) return;
    setActiveSearch(trimmed);
    loadMemories(trimmed);
  }

  function clearSearch() {
    setSearchTerm("");
    setActiveSearch(null);
    loadMemories();
  }

  async function handleCreate(values: MemoryFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await memoryApi.create(values);
      setView({ mode: "idle" });
      await loadMemories(activeSearch ?? undefined);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(memory: Memory, values: MemoryFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await memoryApi.update(memory.id, values);
      setView({ mode: "idle" });
      await loadMemories(activeSearch ?? undefined);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(memory: Memory) {
    if (!confirm("Delete this memory? This cannot be undone.")) return;
    setError(null);
    try {
      await memoryApi.remove(memory.id);
      setMemories((prev) => prev.filter((m) => m.id !== memory.id));
    } catch (err) {
      setError(describeError(err));
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl italic">Memory</h1>
        {view.mode === "idle" && (
          <Button onClick={() => setView({ mode: "creating" })}>
            <Plus />
            New memory
          </Button>
        )}
      </div>

      <form onSubmit={handleSearchSubmit} className="mb-6 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search memories…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        {activeSearch ? (
          <Button type="button" variant="outline" onClick={clearSearch}>
            <X />
            Clear
          </Button>
        ) : (
          <Button type="submit">Search</Button>
        )}
      </form>

      {error && (
        <p className="mb-4 rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
          {error}
        </p>
      )}

      {view.mode === "creating" && (
        <div className="mb-4">
          <MemoryForm
            submitLabel="Create memory"
            isSubmitting={isSubmitting}
            onSubmit={handleCreate}
            onCancel={() => setView({ mode: "idle" })}
          />
        </div>
      )}

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading memories…</p>
      ) : memories.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {activeSearch
            ? `No memories match "${activeSearch}".`
            : "No memories yet. Create your first one above."}
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {memories.map((memory) =>
            view.mode === "editing" && view.memory.id === memory.id ? (
              <MemoryForm
                key={memory.id}
                initial={memory}
                submitLabel="Save changes"
                isSubmitting={isSubmitting}
                onSubmit={(values) => handleUpdate(memory, values)}
                onCancel={() => setView({ mode: "idle" })}
              />
            ) : (
              <MemoryCard
                key={memory.id}
                memory={memory}
                onEdit={() => setView({ mode: "editing", memory })}
                onDelete={() => handleDelete(memory)}
              />
            ),
          )}
        </div>
      )}
    </div>
  );
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong talking to the NEXUS backend.";
}
