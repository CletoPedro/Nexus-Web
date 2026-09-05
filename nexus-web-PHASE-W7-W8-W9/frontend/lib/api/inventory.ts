import { api } from "@/lib/api/client";
import type {
  InventoryItem,
  InventoryItemCreateInput,
  InventoryItemUpdateInput,
} from "@/types/inventory";

function buildQuery(params: Record<string, string | undefined>): string {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v) usp.set(k, v);
  }
  const qs = usp.toString();
  return qs ? `?${qs}` : "";
}

export const inventoryApi = {
  list: (filters?: { category?: string; location?: string }) =>
    api.get<InventoryItem[]>(`/inventory${buildQuery(filters ?? {})}`),
  search: (query: string) =>
    api.get<InventoryItem[]>(`/inventory/search?q=${encodeURIComponent(query)}`),
  get: (id: string) => api.get<InventoryItem>(`/inventory/${id}`),
  create: (input: InventoryItemCreateInput) => api.post<InventoryItem>("/inventory", input),
  update: (id: string, input: InventoryItemUpdateInput) =>
    api.put<InventoryItem>(`/inventory/${id}`, input),
  remove: (id: string) => api.delete<void>(`/inventory/${id}`),
};
