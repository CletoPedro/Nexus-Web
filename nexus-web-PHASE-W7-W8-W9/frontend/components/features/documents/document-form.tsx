"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { Document } from "@/types/document";

export interface DocumentFormValues {
  title: string;
  description: string;
  category: string;
  storage_path: string;
  tags: string[];
  expiry_date: string | null;
  expiry_date_provided: true;
}

export function DocumentForm({
  initial,
  onSubmit,
  onCancel,
  submitLabel,
  isSubmitting,
}: {
  initial?: Document;
  onSubmit: (values: DocumentFormValues) => void;
  onCancel?: () => void;
  submitLabel: string;
  isSubmitting: boolean;
}) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [category, setCategory] = useState(initial?.category ?? "");
  const [storagePath, setStoragePath] = useState(initial?.storage_path ?? "");
  const [tagsText, setTagsText] = useState(initial?.tags.join(", ") ?? "");
  const [expiryDate, setExpiryDate] = useState(initial?.expiry_date?.slice(0, 10) ?? "");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) {
      setError("Document title cannot be empty.");
      return;
    }
    setError(null);
    onSubmit({
      title: trimmed,
      description: description.trim(),
      category: category.trim(),
      storage_path: storagePath.trim(),
      tags: tagsText.split(",").map((t) => t.trim()).filter(Boolean),
      expiry_date: expiryDate || null,
      expiry_date_provided: true,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-[var(--radius-md)] border border-border bg-card p-4"
    >
      <Input
        autoFocus
        placeholder="Document title (e.g. Passport)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Textarea
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={2}
      />
      <Input
        placeholder="Category (e.g. identity, contract, warranty)"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
      />
      <Input
        placeholder="File path (metadata only — not uploaded)"
        value={storagePath}
        onChange={(e) => setStoragePath(e.target.value)}
      />
      <Input
        placeholder="Tags (comma-separated, optional)"
        value={tagsText}
        onChange={(e) => setTagsText(e.target.value)}
      />
      <div>
        <label className="mb-1 block text-xs text-muted-foreground">
          Expiry date (optional)
        </label>
        <Input
          type="date"
          value={expiryDate}
          onChange={(e) => setExpiryDate(e.target.value)}
          className="w-auto"
        />
      </div>
      {error && <p className="text-sm text-highlight">{error}</p>}
      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving…" : submitLabel}
        </Button>
      </div>
    </form>
  );
}
