"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { TASK_PRIORITIES, type Task, type TaskPriority } from "@/types/task";

export interface TaskFormValues {
  title: string;
  description: string;
  priority: TaskPriority;
  due_date: string | null;
  due_date_provided: true;
}

function toDateInputValue(iso: string | null): string {
  if (!iso) return "";
  return iso.slice(0, 10);
}

export function TaskForm({
  initial,
  onSubmit,
  onCancel,
  submitLabel,
  isSubmitting,
}: {
  initial?: Task;
  onSubmit: (values: TaskFormValues) => void;
  onCancel?: () => void;
  submitLabel: string;
  isSubmitting: boolean;
}) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [priority, setPriority] = useState<TaskPriority>(initial?.priority ?? "MEDIUM");
  const [dueDate, setDueDate] = useState(toDateInputValue(initial?.due_date ?? null));
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) {
      setError("Task title cannot be empty.");
      return;
    }
    setError(null);
    onSubmit({
      title: trimmed,
      description: description.trim(),
      priority,
      due_date: dueDate ? new Date(`${dueDate}T23:59:59`).toISOString() : null,
      due_date_provided: true,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-[var(--radius-md)] border border-border bg-card p-4"
    >
      <Input
        autoFocus
        placeholder="Task title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <Textarea
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={2}
      />
      <div className="flex flex-wrap gap-3">
        <Select
          value={priority}
          onChange={(e) => setPriority(e.target.value as TaskPriority)}
          aria-label="Priority"
        >
          {TASK_PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </Select>
        <Input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          aria-label="Due date"
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
