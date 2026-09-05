import { api } from "@/lib/api/client";
import type { TimelineEvent, TimelineFilters } from "@/types/timeline";

export const timelineApi = {
  list: (filters?: TimelineFilters) => {
    const usp = new URLSearchParams();
    if (filters?.event_type) usp.set("event_type", filters.event_type);
    if (filters?.start_date) usp.set("start_date", filters.start_date);
    if (filters?.end_date) usp.set("end_date", filters.end_date);
    const qs = usp.toString();
    return api.get<TimelineEvent[]>(`/timeline${qs ? `?${qs}` : ""}`);
  },
  search: (query: string) =>
    api.get<TimelineEvent[]>(`/timeline/search?q=${encodeURIComponent(query)}`),
};
