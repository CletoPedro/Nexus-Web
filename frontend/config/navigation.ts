import type { LucideIcon } from "lucide-react";
import {
  Archive,
  BrainCircuit,
  CheckSquare,
  Clock,
  Compass,
  FileText,
  Search,
} from "lucide-react";

export interface NavModule {
  /** Route segment under (dashboard), e.g. "memory" -> /memory */
  slug: string;
  /** Label as shown on the index tab. Kept short — reads as a file label. */
  label: string;
  icon: LucideIcon;
}

/**
 * The seven NEXUS modules, in the order they should appear on the index
 * rail. This is the single source of truth for navigation — both the
 * shell and (later) route generation should read from here rather than
 * hardcoding module lists.
 */
export const navModules: NavModule[] = [
  { slug: "now", label: "Now", icon: Compass },
  { slug: "memory", label: "Memory", icon: BrainCircuit },
  { slug: "tasks", label: "Tasks", icon: CheckSquare },
  { slug: "documents", label: "Documents", icon: FileText },
  { slug: "inventory", label: "Inventory", icon: Archive },
  { slug: "timeline", label: "Timeline", icon: Clock },
  { slug: "search", label: "Search", icon: Search },
];
