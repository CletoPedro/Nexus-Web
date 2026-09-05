export type TimelineEventType =
  | "MEMORY_CREATED"
  | "TASK_CREATED"
  | "TASK_COMPLETED"
  | "DOCUMENT_CREATED"
  | "INVENTORY_CREATED"
  | "INVENTORY_UPDATED";

export const TIMELINE_EVENT_TYPES: TimelineEventType[] = [
  "MEMORY_CREATED",
  "TASK_CREATED",
  "TASK_COMPLETED",
  "DOCUMENT_CREATED",
  "INVENTORY_CREATED",
  "INVENTORY_UPDATED",
];

export interface TimelineEvent {
  id: string;
  event_type: TimelineEventType;
  entity_type: string;
  entity_id: string;
  title: string;
  occurred_at: string | null;
  created_at: string | null;
}

export interface TimelineFilters {
  event_type?: TimelineEventType;
  start_date?: string;
  end_date?: string;
}
