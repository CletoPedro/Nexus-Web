"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navModules } from "@/config/navigation";
import { cn } from "@/lib/utils";

/** Horizontal scrollable module strip shown below md; NavRail is hidden there. */
export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="NEXUS modules"
      className="flex md:hidden overflow-x-auto border-b border-border bg-card px-2"
    >
      {navModules.map((mod) => {
        const href = `/${mod.slug}`;
        const isActive = pathname === href || pathname.startsWith(`${href}/`);
        const Icon = mod.icon;

        return (
          <Link
            key={mod.slug}
            href={href}
            aria-current={isActive ? "page" : undefined}
            className={cn(
              "flex shrink-0 flex-col items-center gap-1 border-b-2 px-3 py-2 text-[11px]",
              isActive
                ? "border-accent text-foreground font-medium"
                : "border-transparent text-muted-foreground",
            )}
          >
            <Icon className="size-4" />
            {mod.label}
          </Link>
        );
      })}
    </nav>
  );
}
