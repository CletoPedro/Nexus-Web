# PHASE W11 — NOW Dashboard

**Status:** Implementada e verificada end-to-end (browser real, backend real, PostgreSQL real).

## Objetivo
Transformar `/now` de placeholder na página inicial operacional real: "o que está a acontecer agora".

## Arquitetura
- `NowService` compõe os serviços já existentes (Task/Memory/Document/Inventory/Timeline) — zero duplicação de lógica de query.
- Classificação de tarefas: overdue (usa `Task.is_overdue()` já existente), high-priority (HIGH/CRITICAL, excluindo já-overdue para não duplicar), upcoming (dentro da janela configurável, excluindo overdue).
- `GET /api/v1/now` devolve tudo num único payload (overdue/high-priority/upcoming tasks + recent memory/documents/inventory/timeline).

## Ficheiros criados
```
backend: domain/now/entity.py, services/now_service.py,
         api/v1/schemas/now.py, api/v1/now.py,
         tests/test_now_api.py (11 testes)
frontend: types/now.ts, lib/api/now.ts,
          components/ui/modal.tsx (genérico, reutilizado),
          components/features/now/{now-section,task-row,memory-row,
            document-row,inventory-row,timeline-row,quick-actions}.tsx,
          app/(dashboard)/now/page.tsx (substitui placeholder)
```

## Ficheiros modificados
`api/v1/router.py` — registado o router de now.

## Testes (11, todos reais contra Postgres)
Tarefa overdue aparece na secção certa; concluída deixa de aparecer; high-priority correto; overdue+critical aparece só em overdue (nunca duplicado); upcoming dentro/fora da janela; recent memory/documents/inventory/timeline refletem criações reais; `recent_limit` respeitado.

## Frontend
Seis secções (Today, Recent Memory, Recent Documents, Inventory, Timeline, Quick Actions), todas com componentes reutilizáveis (rows compactas, não duplicam os cartões completos de Memory/Tasks/etc). Quick Actions reutiliza os formulários já existentes (`MemoryForm`, `TaskForm`, `DocumentForm`, `InventoryForm`) dentro de um modal genérico partilhado — nenhum formulário novo foi criado.

## Verificação E2E real
Screenshots em `docs/phases/screenshots-w11/`: dashboard completo, clique numa tarefa navega para `/tasks`, quick action "Memory" cria e atualiza o dashboard imediatamente, mobile e dark mode confirmados.

## Lint/Build
`pnpm lint` → 0 erros à primeira. `pnpm build` → sucesso.

## Problemas conhecidos
Sem paginação nas secções "Recent" (mostra sempre os N mais recentes, configurável via query param mas sem UI de "carregar mais").
