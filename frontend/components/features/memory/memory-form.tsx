"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { Memory } from "@/types/memory";

export interface MemoryFormValues {
  content: string;
  tags: string[];
}

export function MemoryForm({
  initial,
  onSubmit,
  onCancel,
  submitLabel,
  isSubmitting,
}: {
  initial?: Memory;
  onSubmit: (values: MemoryFormValues) => void;
  onCancel?: () => void;
  submitLabel: string;
  isSubmitting: boolean;
}) {
  const [content, setContent] = useState(initial?.content ?? "");
  const [tagsText, setTagsText] = useState(initial?.tags.join(", ") ?? "");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) {
      setError("Memory content cannot be empty.");
      return;
    }
    setError(null);
    const tags = tagsText
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    onSubmit({ content: trimmed, tags });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-[var(--radius-md)] border border-border bg-card p-4"
    >
      <Textarea
        autoFocus
        placeholder="Remember that..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={3}
      />
      <Input
        placeholder="Tags (comma-separated, optional)"
        value={tagsText}
        onChange={(e) => setTagsText(e.target.value)}
      />
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
