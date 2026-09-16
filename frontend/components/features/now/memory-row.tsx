import Link from "next/link";

import type { Memory } from "@/types/memory";

export function MemoryRow({ memory }: { memory: Memory }) {
  return (
    <Link
      href="/memory"
      className="block truncate rounded-[var(--radius-sm)] border border-border px-3 py-2 text-sm hover:bg-muted"
    >
      {memory.content}
    </Link>
  );
}
