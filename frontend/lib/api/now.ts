import { api } from "@/lib/api/client";
import type { NowSnapshot } from "@/types/now";

export const nowApi = {
  get: () => api.get<NowSnapshot>("/now"),
};
