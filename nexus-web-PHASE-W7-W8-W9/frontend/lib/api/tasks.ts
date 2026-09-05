import { api } from "@/lib/api/client";
import type {
  Task,
  TaskCreateInput,
  TaskListFilters,
  TaskStatus,
  TaskUpdateInput,
} from "@/types/task";

function buildQuery(filters?: TaskListFilters): string {
  if (!filters) return "";
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.overdue) params.set("overdue", "true");
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const taskApi = {
  list: (filters?: TaskListFilters) => api.get<Task[]>(`/tasks${buildQuery(filters)}`),
  search: (query: string) => api.get<Task[]>(`/tasks/search?q=${encodeURIComponent(query)}`),
  get: (id: string) => api.get<Task>(`/tasks/${id}`),
  create: (input: TaskCreateInput) => api.post<Task>("/tasks", input),
  update: (id: string, input: TaskUpdateInput) => api.put<Task>(`/tasks/${id}`, input),
  setStatus: (id: string, status: TaskStatus) =>
    api.put<Task>(`/tasks/${id}/status`, { status }),
  remove: (id: string) => api.delete<void>(`/tasks/${id}`),
};
