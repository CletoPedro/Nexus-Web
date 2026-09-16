"use client";

import { Search } from "lucide-react";
import { useEffect, useState } from "react";

import { GlobalSearchDialog } from "@/components/features/search/global-search-dialog";
import { Button } from "@/components/ui/button";

export function GlobalSearchTrigger() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const isShortcut = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k";
      if (isShortcut) {
        e.preventDefault();
        setOpen(true);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <>
      {/* Desktop: a search-field-styled trigger with a visible shortcut hint */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="hidden md:flex items-center gap-2 rounded-[var(--radius-sm)] border border-border bg-background px-3 py-1.5 text-sm text-muted-foreground hover:border-accent/50 min-w-[220px]"
      >
        <Search className="size-4 shrink-0" />
        <span className="flex-1 text-left">Search your NEXUS</span>
        <kbd className="rounded border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px]">
          ⌘K
        </kbd>
      </button>

      {/* Mobile: icon only, keeps the topbar compact */}
      <Button
        variant="ghost"
        size="icon"
        aria-label="Search NEXUS"
        className="md:hidden"
        onClick={() => setOpen(true)}
      >
        <Search />
      </Button>

      <GlobalSearchDialog open={open} onClose={() => setOpen(false)} />
    </>
  );
}
