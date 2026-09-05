"use client";

import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { TimelineItem } from "@/components/features/timeline/timeline-item";
import { ApiError } from "@/lib/api/client";
import { timelineApi } from "@/lib/api/timeline";
import { TIMELINE_EVENT_TYPES, type TimelineEvent, type TimelineEventType } from "@/types/timeline";

export default function TimelinePage() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [eventType, setEventType] = useState<TimelineEventType | "">("");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeSearch, setActiveSearch] = useState<string | null>(null);

  async function loadEvents() {
    setLoading(true);
    setError(null);
    try {
      const data = activeSearch
        ? await timelineApi.search(activeSearch)
        : await timelineApi.list(eventType ? { event_type: eventType } : undefined);
      setEvents(data);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [eventType, activeSearch]);

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

  return (
    <div className="max-w-2xl">
      <h1 className="mb-6 font-display text-3xl italic">Timeline</h1>

      <form onSubmit={handleSearchSubmit} className="mb-4 flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search timeline…"
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

      {!activeSearch && (
        <div className="mb-6">
          <Select
            value={eventType}
            onChange={(e) => setEventType(e.target.value as TimelineEventType | "")}
            aria-label="Filter by event type"
          >
            <option value="">All events</option>
            {TIMELINE_EVENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.replaceAll("_", " ")}
              </option>
            ))}
          </Select>
        </div>
      )}

      {error && (
        <p className="mb-4 rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-muted-foreground">Loading timeline…</p>
      ) : events.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          {activeSearch
            ? `No events match "${activeSearch}".`
            : "No events yet. Create a memory, task, document, or inventory item to see it here."}
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {events.map((event) => (
            <TimelineItem key={event.id} event={event} />
          ))}
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
