"use client";

import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { TASK_PRIORITIES, TASK_STATUSES, type TaskListFilters } from "@/types/task";

export function TaskFilters({
  filters,
  onChange,
}: {
  filters: TaskListFilters;
  onChange: (filters: TaskListFilters) => void;
}) {
  const hasActiveFilters = !!(filters.status || filters.priority || filters.overdue);

  return (
    <div className="mb-6 flex flex-wrap items-center gap-2">
      <Select
        value={filters.status ?? ""}
        onChange={(e) =>
          onChange({
            ...filters,
            status: (e.target.value || undefined) as TaskListFilters["status"],
          })
        }
        aria-label="Filter by status"
      >
        <option value="">All statuses</option>
        {TASK_STATUSES.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </Select>

      <Select
        value={filters.priority ?? ""}
        onChange={(e) =>
          onChange({
            ...filters,
            priority: (e.target.value || undefined) as TaskListFilters["priority"],
          })
        }
        aria-label="Filter by priority"
      >
        <option value="">All priorities</option>
        {TASK_PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </Select>

      <Button
        type="button"
        variant={filters.overdue ? "highlight" : "outline"}
        size="sm"
        onClick={() => onChange({ ...filters, overdue: !filters.overdue })}
      >
        Overdue
      </Button>

      {hasActiveFilters && (
        <Button type="button" variant="ghost" size="sm" onClick={() => onChange({})}>
          Clear filters
        </Button>
      )}
    </div>
  );
}
