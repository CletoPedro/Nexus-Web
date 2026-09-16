import Link from "next/link";

import type { Document } from "@/types/document";

export function DocumentRow({ document }: { document: Document }) {
  return (
    <Link
      href="/documents"
      className="flex items-center gap-2 truncate rounded-[var(--radius-sm)] border border-border px-3 py-2 text-sm hover:bg-muted"
    >
      <span className="min-w-0 flex-1 truncate">{document.title}</span>
      {document.category && (
        <span className="shrink-0 rounded-full bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
          {document.category}
        </span>
      )}
    </Link>
  );
}
