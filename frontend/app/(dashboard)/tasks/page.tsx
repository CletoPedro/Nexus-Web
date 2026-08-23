"use client";

import { Plus, Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { TaskCard } from "@/components/features/tasks/task-card";
import { TaskFilters } from "@/components/features/tasks/task-filters";
import { TaskForm, type TaskFormValues } from "@/components/features/tasks/task-form";
import { ApiError } from "@/lib/api/client";
import { taskApi } from "@/lib/api/tasks";
import type { Task, TaskListFilters, TaskStatus } from "@/types/task";

type ViewState = { mode: "idle" } | { mode: "creating" } | { mode: "editing"; task: Task };

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<ViewState>({ mode: "idle" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [filters, setFilters] = useState<TaskListFilters>({});
  const [searchTerm, setSearchTerm] = useState("");
  const [activeSearch, setActiveSearch] = useState<string | null>(null);

  async function loadTasks() {
    setLoading(true);
    setError(null);
    try {
      const data = activeSearch ? await taskApi.search(activeSearch) : await taskApi.list(filters);
      setTasks(data);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, activeSearch]);

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

  async function handleCreate(values: TaskFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await taskApi.create(values);
      setView({ mode: "idle" });
      await loadTasks();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(task: Task, values: TaskFormValues) {
    setIsSubmitting(true);
    setError(null);
    try {
      await taskApi.update(task.id, values);
      setView({ mode: "idle" });
      await loadTasks();
    } catch (err) {
      setError(describeError(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSetStatus(task: Task, status: TaskStatus) {
    setError(null);
    try {
      const updated = await taskApi.setStatus(task.id, status);
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (err) {
      setError(describeError(err));
    }
  }

  async function handleDelete(task: Task) {
    if (!confirm("Delete this task? This cannot be undone.")) return;
    setError(null);
    try {
      await taskApi.remove(task.id);
      setTasks((prev) => prev.filter((t) => t.id !== task.id));
    } catch (err) {
      setError(describeError(err));
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl italic">Tasks</h1>
        {view.mode === "idle" && (
          <Button onClick={() => setView({ mode: "creating" })}>
            <Plus />
            New task
          </Button>
        )}
      </div>

      <form onSubmit={handleSearchSubmit} className="mb-4 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search tasks…"
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

      {!activeSearch && <TaskFilters filters={filters} onChange={setFilters} />}

      {error && (
        <p className="mb-4 rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
          {error}
        </p>
      )}

      {view.mode === "creating" && (
        <div className="mb-4">
          <TaskForm
            submitLabel="Create task"
            isSubmitting={isSubmitting}
            onSubmit={handleCreate}
            onCancel={() => setView({ mode: "idle" })}
          />
        </div>
      )}

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading tasks…</p>
      ) : tasks.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {activeSearch
            ? `No tasks match "${activeSearch}".`
            : "No tasks yet. Create your first one above."}
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {tasks.map((task) =>
            view.mode === "editing" && view.task.id === task.id ? (
              <TaskForm
                key={task.id}
                initial={task}
                submitLabel="Save changes"
                isSubmitting={isSubmitting}
                onSubmit={(values) => handleUpdate(task, values)}
                onCancel={() => setView({ mode: "idle" })}
              />
            ) : (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={() => setView({ mode: "editing", task })}
                onDelete={() => handleDelete(task)}
                onSetStatus={(status) => handleSetStatus(task, status)}
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
