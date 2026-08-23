interface ModulePlaceholderProps {
  title: string;
  phase: string;
  description: string;
}

/**
 * Placeholder for a module route that exists only to prove navigation in
 * Phase W2. Each module gets real content in its own implementation phase
 * (see docs/architecture/PHASE_W1_ARCHITECTURE.md, section 10 — roadmap).
 * This is an explicit, labeled placeholder — never a fake result.
 */
export function ModulePlaceholder({
  title,
  phase,
  description,
}: ModulePlaceholderProps) {
  return (
    <div className="max-w-2xl">
      <p className="font-mono text-xs text-muted-foreground tracking-wide mb-2">
        {phase} · NOT YET IMPLEMENTED
      </p>
      <h1 className="font-display text-3xl italic mb-3">{title}</h1>
      <p className="text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}
