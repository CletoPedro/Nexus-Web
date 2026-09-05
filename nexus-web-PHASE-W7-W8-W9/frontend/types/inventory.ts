export interface InventoryItem {
  id: string;
  name: string;
  description: string;
  category: string;
  location: string;
  quantity: number;
  purchase_date: string | null;
  purchase_price: string | null;
  serial_number: string;
  document_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface InventoryItemCreateInput {
  name: string;
  description?: string;
  category?: string;
  location?: string;
  quantity?: number;
  purchase_date?: string | null;
  purchase_price?: string | null;
  serial_number?: string;
  document_id?: string | null;
}

export interface InventoryItemUpdateInput {
  name: string;
  description?: string;
  category?: string;
  location?: string;
  quantity?: number;
  document_id?: string | null;
  document_id_provided?: boolean;
}
