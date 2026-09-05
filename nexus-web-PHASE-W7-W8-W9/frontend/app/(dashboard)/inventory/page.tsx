"use client";

import { Plus, Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { InventoryCard } from "@/components/features/inventory/inventory-card";
import {
  InventoryForm,
  type InventoryFormValues,
} from "@/components/features/inventory/inventory-form";
import { ApiError } from "@/lib/api/client";
import { documentApi } from "@/lib/api/documents";
import { inventoryApi } from "@/lib/api/inventory";
import type { Document } from "@/types/document";
import type { InventoryItem } from "@/types/inventory";

type ViewState = { mode: "idle" } | { mode: "creating" } | { mode: "editing"; item: InventoryItem };

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewState>({ mode: "idle" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [category, setCategory] = useState("");
  const [location, setLocation] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeSearch, setActiveSearch] = useState<string | null>(null);

  async function loadItems() {
    setLoading(true);
    setError(null);
    try {
      const data = activeSearch
        ? await inventoryApi.search(activeSearch)
        : await inventoryApi.list({
            category: category || undefined,
            location: location || undefined,
          });
      setItems(data);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, location, activeSearch]);

  useEffect(() => {
    documentApi.list().then(setDocuments).catch(() => setDocuments([]));
  }, []);

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = searchTerm.trim();
    if (!trimmed) return;
    setActiveSearch(trimmed);
  }

  function clearSearch() {
    setSearchTerm("");
    setActiveSearch(null);
  }

  async function handleCreate(values: InventoryFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await inventoryApi.create(values);
      setView({ mode: "idle" });
      await loadItems();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(item: InventoryItem, values: InventoryFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await inventoryApi.update(item.id, values);
      setView({ mode: "idle" });
      await loadItems();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(item: InventoryItem) {
    if (!confirm("Delete this item? This cannot be undone.")) return;
    setError(null);
    try {
      await inventoryApi.remove(item.id);
      setItems((prev) => prev.filter((i) => i.id !== item.id));
    } catch (err) {
      setError(describeError(err));
    }
  }

  function documentTitleFor(id: string | null): string | undefined {
    if (!id) return undefined;
    return documents.find((d) => d.id === id)?.title;
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl italic">Inventory</h1>
        {view.mode === "idle" && (
          <Button onClick={() => setView({ mode: "creating" })}>
            <Plus />
            New item
          </Button>
        )}
      </div>

      <form onSubmit={handleSearchSubmit} className="mb-4 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search inventory…"
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

      {!activeSearch && (
        <div className="mb-6 flex flex-wrap items-center gap-2">
          <Input
            placeholder="Filter by category…"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="max-w-[180px]"
          />
          <Input
            placeholder="Filter by location…"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="max-w-[180px]"
          />
          {(category || location) && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => {
                setCategory("");
                setLocation("");
              }}
            >
              Clear filters
            </Button>
          )}
        </div>
      )}

      {error && (
        <p className="mb-4 rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
          {error}
        </p>
      )}

      {view.mode === "creating" && (
        <div className="mb-4">
          <InventoryForm
            documents={documents}
            submitLabel="Create item"
            isSubmitting={isSubmitting}
            onSubmit={handleCreate}
            onCancel={() => setView({ mode: "idle" })}
          />
        </div>
      )}

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading inventory…</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {activeSearch
            ? `No items match "${activeSearch}".`
            : "No items yet. Create your first one above."}
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {items.map((item) =>
            view.mode === "editing" && view.item.id === item.id ? (
              <InventoryForm
                key={item.id}
                initial={item}
                documents={documents}
                submitLabel="Save changes"
                isSubmitting={isSubmitting}
                onSubmit={(values) => handleUpdate(item, values)}
                onCancel={() => setView({ mode: "idle" })}
              />
            ) : (
              <InventoryCard
                key={item.id}
                item={item}
                linkedDocumentTitle={documentTitleFor(item.document_id)}
                onEdit={() => setView({ mode: "editing", item })}
                onDelete={() => handleDelete(item)}
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
