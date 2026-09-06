"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { Document } from "@/types/document";
import type { InventoryItem } from "@/types/inventory";

export interface InventoryFormValues {
  name: string;
  description: string;
  category: string;
  location: string;
  quantity: number;
  document_id: string | null;
  document_id_provided: true;
}

export function InventoryForm({
  initial,
  documents,
  onSubmit,
  onCancel,
  submitLabel,
  isSubmitting,
}: {
  initial?: InventoryItem;
  documents: Document[];
  onSubmit: (values: InventoryFormValues) => void;
  onCancel?: () => void;
  submitLabel: string;
  isSubmitting: boolean;
}) {
  const [name, setName] = useState(initial?.name ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [category, setCategory] = useState(initial?.category ?? "");
  const [location, setLocation] = useState(initial?.location ?? "");
  const [quantity, setQuantity] = useState(String(initial?.quantity ?? 1));
  const [documentId, setDocumentId] = useState(initial?.document_id ?? "");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Item name cannot be empty.");
      return;
    }
    const qty = Number(quantity);
    if (!Number.isInteger(qty) || qty < 0) {
      setError("Quantity must be a non-negative whole number.");
      return;
    }
    setError(null);
    onSubmit({
      name: trimmed,
      description: description.trim(),
      category: category.trim(),
      location: location.trim(),
      quantity: qty,
      document_id: documentId || null,
      document_id_provided: true,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-[var(--radius-md)] border border-border bg-card p-4"
    >
      <Input
        autoFocus
        placeholder="Item name (e.g. Laptop)"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <Textarea
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={2}
      />
      <div className="flex flex-wrap gap-3">
        <Input
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="max-w-[180px]"
        />
        <Input
          placeholder="Location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="max-w-[180px]"
        />
        <Input
          type="number"
          min={0}
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          aria-label="Quantity"
          className="w-24"
        />
      </div>
      <Select
        value={documentId}
        onChange={(e) => setDocumentId(e.target.value)}
        aria-label="Linked document"
      >
        <option value="">No linked document</option>
        {documents.map((doc) => (
          <option key={doc.id} value={doc.id}>
            {doc.title}
          </option>
        ))}
      </Select>
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
