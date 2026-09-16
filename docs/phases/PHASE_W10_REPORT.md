# PHASE W10 — Global Search

**Status:** Implementada e verificada end-to-end (browser real, backend real, PostgreSQL real).

## Objetivo
Pesquisa global real, sem IA, sobre Memory/Tasks/Documents/Inventory, agrupada e ordenada por relevância.

## Arquitetura
- Sem repositório próprio: `SearchService` compõe os métodos `search_with_rank()` já existentes (aditivos, não substituem `search()`) em cada um dos quatro repositórios — zero duplicação de lógica de pesquisa.
- Chamadas sequenciais, não `asyncio.gather`: uma `AsyncSession` do SQLAlchemy não é segura para uso concorrente por múltiplas coroutines partilhando a mesma sessão.
- `GET /api/v1/search?q=...&limit=...` devolve `{query, total, memory[], tasks[], documents[], inventory[]}`, cada item com `id, type, title, content, relevance, created_at, target_url`.

## Ficheiros criados
```
backend: domain/search/entity.py, services/search_service.py,
         api/v1/schemas/search.py, api/v1/search.py,
         tests/test_search_api.py (6 testes)
frontend: types/search.ts, lib/api/search.ts,
          components/features/search/{global-search-dialog,search-results-list}.tsx,
          components/layout/global-search-trigger.tsx,
          app/(dashboard)/search/page.tsx (substitui placeholder)
```

## Ficheiros modificados
- `domain/{memory,tasks,documents,inventory}/repository.py` + implementações Postgres — adicionado `search_with_rank()`
- `api/v1/router.py` — registado o router de search
- `components/layout/app-shell.tsx` — adicionado o trigger de pesquisa ao topbar

## Testes (6, todos reais contra Postgres)
Pesquisa vazia devolve grupos vazios; sem resultados; pesquisa cruzada encontra os 4 tipos numa só query; ranking real por relevância (ordem decrescente confirmada); `limit` respeitado; itens com soft-delete nunca aparecem.

## Frontend
Diálogo tipo "command palette" (`⌘K`/`Ctrl+K`), trigger no topbar (campo no desktop, ícone no mobile), página `/search` de página inteira partilhando o componente de resultados com o diálogo.

## Verificação E2E real
Screenshots em `docs/phases/screenshots-w10/`: grupos corretos, "No results found", Escape fecha, Ctrl+K abre, clique navega para o módulo certo, mobile funcional sem quebrar a nav shell.

## Lint/Build
`pnpm lint` → 0 erros. `pnpm build` → sucesso.

## Problemas conhecidos
`target_url` aponta para a página do módulo (não existe página de detalhe por item ainda) — limitação documentada, não uma simulação.
