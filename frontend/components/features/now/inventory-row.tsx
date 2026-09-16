import Link from "next/link";

import type { InventoryItem } from "@/types/inventory";

export function InventoryRow({ item }: { item: InventoryItem }) {
  return (
    <Link
      href="/inventory"
      className="flex items-center gap-2 truncate rounded-[var(--radius-sm)] border border-border px-3 py-2 text-sm hover:bg-muted"
    >
      <span className="min-w-0 flex-1 truncate">{item.name}</span>
      {item.location && (
        <span className="shrink-0 rounded-full bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
          {item.location}
        </span>
      )}
    </Link>
  );
}
