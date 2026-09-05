export interface Document {
  id: string;
  title: string;
  description: string;
  category: string;
  file_name: string;
  file_type: string;
  file_size: number | null;
  storage_path: string;
  tags: string[];
  expiry_date: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface DocumentCreateInput {
  title: string;
  description?: string;
  category?: string;
  file_name?: string;
  file_type?: string;
  file_size?: number | null;
  storage_path?: string;
  tags?: string[];
  expiry_date?: string | null;
}

export interface DocumentUpdateInput {
  title: string;
  description?: string;
  category?: string;
  tags?: string[];
  expiry_date?: string | null;
  expiry_date_provided?: boolean;
}
