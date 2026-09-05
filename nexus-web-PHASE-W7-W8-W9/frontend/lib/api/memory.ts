import { api } from "@/lib/api/client";
import type { Memory, MemoryCreateInput, MemoryUpdateInput } from "@/types/memory";

export const memoryApi = {
  list: () => api.get<Memory[]>("/memories"),
  search: (query: string) =>
    api.get<Memory[]>(`/memories/search?q=${encodeURIComponent(query)}`),
  get: (id: string) => api.get<Memory>(`/memories/${id}`),
  create: (input: MemoryCreateInput) => api.post<Memory>("/memories", input),
  update: (id: string, input: MemoryUpdateInput) =>
    api.put<Memory>(`/memories/${id}`, input),
  remove: (id: string) => api.delete<void>(`/memories/${id}`),
};
