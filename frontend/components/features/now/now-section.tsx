import Link from "next/link";
import type { ReactNode } from "react";

export function NowSection({
  title,
  viewAllHref,
  isEmpty,
  emptyText,
  children,
}: {
  title: string;
  viewAllHref: string;
  isEmpty: boolean;
  emptyText: string;
  children: ReactNode;
}) {
  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="font-mono text-xs uppercase tracking-wide text-muted-foreground">
          {title}
        </h2>
        <Link
          href={viewAllHref}
          className="font-mono text-xs text-muted-foreground hover:text-accent"
        >
          View all →
        </Link>
      </div>
      {isEmpty ? (
        <p className="text-sm text-muted-foreground">{emptyText}</p>
      ) : (
        <div className="flex flex-col gap-2">{children}</div>
      )}
    </section>
  );
}
