/**
 * Mirrors app/api/v1/schemas/memory.py on the backend. Kept manually in
 * sync for now; generating these from the backend's OpenAPI schema is a
 * candidate improvement for a later phase.
 */
export interface Memory {
  id: string;
  content: string;
  tags: string[];
  metadata: Record<string, unknown>;
  created_at: string | null;
  updated_at: string | null;
}

export interface MemoryCreateInput {
  content: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface MemoryUpdateInput {
  content: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}
