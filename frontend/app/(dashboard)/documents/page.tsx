"use client";

import { Plus, Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DocumentCard } from "@/components/features/documents/document-card";
import {
  DocumentForm,
  type DocumentFormValues,
} from "@/components/features/documents/document-form";
import { ApiError } from "@/lib/api/client";
import { documentApi } from "@/lib/api/documents";
import type { Document } from "@/types/document";

type ViewState = { mode: "idle" } | { mode: "creating" } | { mode: "editing"; document: Document };

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewState>({ mode: "idle" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [category, setCategory] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeSearch, setActiveSearch] = useState<string | null>(null);

  async function loadDocuments() {
    setLoading(true);
    setError(null);
    try {
      const data = activeSearch
        ? await documentApi.search(activeSearch)
        : await documentApi.list(category || undefined);
      setDocuments(data);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, activeSearch]);

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

  async function handleCreate(values: DocumentFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await documentApi.create(values);
      setView({ mode: "idle" });
      await loadDocuments();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(document: Document, values: DocumentFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await documentApi.update(document.id, values);
      setView({ mode: "idle" });
      await loadDocuments();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(document: Document) {
    if (!confirm("Delete this document? This cannot be undone.")) return;
    setError(null);
    try {
      await documentApi.remove(document.id);
      setDocuments((prev) => prev.filter((d) => d.id !== document.id));
    } catch (err) {
      setError(describeError(err));
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl italic">Documents</h1>
        {view.mode === "idle" && (
          <Button onClick={() => setView({ mode: "creating" })}>
            <Plus />
            New document
          </Button>
        )}
      </div>

      <p className="mb-4 text-xs text-muted-foreground">
        File paths are stored as metadata only — NEXUS does not upload or store the
        actual file yet.
      </p>

      <form onSubmit={handleSearchSubmit} className="mb-4 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search documents…"
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
        <div className="mb-6 flex items-center gap-2">
          <Input
            placeholder="Filter by category…"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="max-w-xs"
          />
          {category && (
            <Button type="button" variant="ghost" size="sm" onClick={() => setCategory("")}>
              Clear filter
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
          <DocumentForm
            submitLabel="Create document"
            isSubmitting={isSubmitting}
            onSubmit={handleCreate}
            onCancel={() => setView({ mode: "idle" })}
          />
        </div>
      )}

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading documents…</p>
      ) : documents.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {activeSearch
            ? `No documents match "${activeSearch}".`
            : "No documents yet. Create your first one above."}
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {documents.map((document) =>
            view.mode === "editing" && view.document.id === document.id ? (
              <DocumentForm
                key={document.id}
                initial={document}
                submitLabel="Save changes"
                isSubmitting={isSubmitting}
                onSubmit={(values) => handleUpdate(document, values)}
                onCancel={() => setView({ mode: "idle" })}
              />
            ) : (
              <DocumentCard
                key={document.id}
                document={document}
                onEdit={() => setView({ mode: "editing", document })}
                onDelete={() => handleDelete(document)}
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
