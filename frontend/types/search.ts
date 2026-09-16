export type SearchResultType = "memory" | "task" | "document" | "inventory";

export interface SearchResult {
  id: string;
  type: SearchResultType;
  title: string;
  content: string;
  relevance: number;
  created_at: string | null;
  target_url: string;
}

export interface SearchResponse {
  query: string;
  total: number;
  memory: SearchResult[];
  tasks: SearchResult[];
  documents: SearchResult[];
  inventory: SearchResult[];
}
