/**
 * Mirrors app/api/v1/schemas/task.py on the backend. Kept manually in
 * sync, same as types/memory.ts.
 */
export type TaskStatus = "TODO" | "IN_PROGRESS" | "DONE" | "CANCELLED";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export const TASK_STATUSES: TaskStatus[] = [
  "TODO",
  "IN_PROGRESS",
  "DONE",
  "CANCELLED",
];

export const TASK_PRIORITIES: TaskPriority[] = [
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL",
];

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  completed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string | null;
}

export interface TaskUpdateInput {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string | null;
  due_date_provided?: boolean;
}

export interface TaskListFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  overdue?: boolean;
}
