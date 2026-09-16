import { api } from "@/lib/api/client";
import type { SearchResponse } from "@/types/search";

export const globalSearchApi = {
  search: (query: string, limit = 20) =>
    api.get<SearchResponse>(
      `/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    ),
};
