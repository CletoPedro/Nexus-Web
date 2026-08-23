# NEXUS — Frontend

Next.js (App Router) + TypeScript + Tailwind v4 frontend for NEXUS WEB.
See `/docs/architecture/PHASE_W1_ARCHITECTURE.md` at the repo root for the
full architecture and `/docs/phases/` for phase-by-phase reports.

## Stack

- Next.js 16 (App Router, Turbopack)
- TypeScript
- Tailwind CSS v4
- shadcn/ui primitives (hand-authored; `ui.shadcn.com` registry is not
  reachable from the dev sandbox — see PHASE_W2 report for detail)
- next-themes (dark/light mode)
- Self-hosted fonts via `@fontsource` (Fraunces, Inter, IBM Plex Mono)

## Commands

```bash
pnpm install
pnpm dev      # http://localhost:3000
pnpm lint
pnpm build
pnpm start
```

## Structure

- `app/(dashboard)/` — the seven NEXUS modules (now, memory, tasks,
  documents, inventory, timeline, search), each behind the shared shell
- `app/(auth)/` — reserved for the Security phase; empty until then
- `components/layout/` — app shell, nav rail, theme provider/toggle
- `components/ui/` — shadcn-style primitives
- `components/features/` — domain-specific components (currently just the
  module placeholder)
- `lib/api/` — the only permitted path to the backend (placeholder until
  Phase W3+)
- `config/navigation.ts` — single source of truth for the module list
