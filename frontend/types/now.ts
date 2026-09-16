import type { Document } from "@/types/document";
import type { InventoryItem } from "@/types/inventory";
import type { Memory } from "@/types/memory";
import type { Task } from "@/types/task";
import type { TimelineEvent } from "@/types/timeline";

export interface NowSnapshot {
  overdue_tasks: Task[];
  high_priority_tasks: Task[];
  upcoming_tasks: Task[];
  recent_memories: Memory[];
  recent_documents: Document[];
  recent_inventory: InventoryItem[];
  recent_timeline: TimelineEvent[];
}
