import { api } from "@/lib/api/client";
import type { Document, DocumentCreateInput, DocumentUpdateInput } from "@/types/document";

export const documentApi = {
  list: (category?: string) =>
    api.get<Document[]>(`/documents${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  search: (query: string) => api.get<Document[]>(`/documents/search?q=${encodeURIComponent(query)}`),
  get: (id: string) => api.get<Document>(`/documents/${id}`),
  create: (input: DocumentCreateInput) => api.post<Document>("/documents", input),
  update: (id: string, input: DocumentUpdateInput) => api.put<Document>(`/documents/${id}`, input),
  remove: (id: string) => api.delete<void>(`/documents/${id}`),
};
