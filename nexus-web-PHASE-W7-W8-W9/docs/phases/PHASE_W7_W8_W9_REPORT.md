# PHASE W7 + W8 + W9 — Documents, Inventory, Timeline

**Status:** Implementado e verificado end-to-end (browser real, backend real, PostgreSQL real). Aguarda aprovação.
**Impacto em produção:** **nenhum ainda** — ver secção 9. Este trabalho existe apenas nesta sandbox; o push para `CletoPedro/Nexus-Web` continua pendente da tua decisão de credenciais.

---

## 1. Desvio importante face à especificação (documentado, não ignorado)

O documento de especificação afirma: *"TimelineEvent table already exists. Use it."* **Isto não é verdade nesta base de código.** Não existia nenhuma tabela, modelo, domínio, ou API de Timeline antes desta fase — apenas a página placeholder do frontend (W2). Tratei isto como um desvio a documentar explicitamente, não como um facto silenciosamente assumido: criei a tabela `timeline_events` de raiz nesta fase, via migração normal. Como não existia nada antes, não há risco de perda de dados.

---

## 2. Arquitetura — decisões

- Mesma disciplina de W4.5/W6: `domain/` sem dependências de framework; `api/` só importa `services`, nunca `repositories` diretamente; fábricas de DI vivem em `services/*.py`.
- **Integração da Timeline feita na camada API, não dentro dos serviços de Memory/Tasks.** Em vez de modificar `memory_service.py` ou `task_service.py` para conhecerem a Timeline (o que violaria a separação de responsabilidades e arriscaria regressões nesses serviços já testados), os routers (`api/v1/memory.py`, `api/v1/tasks.py`) passaram a depender também de `TimelineService`, e chamam `timeline.record(...)` depois de uma criação/conclusão bem-sucedida. Isto respeita a regra "não modificar o comportamento existente de Memory/Tasks exceto onde a integração o exigir" da forma mais restrita possível: **zero linhas alteradas em `memory_service.py` e `task_service.py`**, e os 25 testes originais continuam a passar sem qualquer alteração.
- `Inventory.document_id` é uma FK real para `documents.id` (`ON DELETE SET NULL`) — validada no `InventoryService` antes de gravar (rejeita referências a documentos inexistentes com 422).
- `TimelineEventModel` não usa o `AuditMixin` partilhado — é deliberadamente um log de eventos apenas de acrescento (sem `update`, sem soft delete): um evento aconteceu ou não aconteceu.
- **Armazenamento de ficheiros (W7):** `storage_path` é só metadados — uma string que o utilizador fornece. NEXUS não faz upload, não lê, nem serve os bytes reais do ficheiro. Isto é uma limitação explícita e documentada (secção 7), não uma simulação de cloud storage.

---

## 3. Ficheiros criados

### Backend — Documents (W7)
```
app/domain/documents/{entity.py, repository.py}
app/db/models/document.py
app/repositories/document_repository.py
app/services/document_service.py
app/api/v1/schemas/document.py
app/api/v1/documents.py
tests/test_document_api.py (8 testes)
```

### Backend — Inventory (W8)
```
app/domain/inventory/{entity.py, repository.py}
app/db/models/inventory_item.py
app/repositories/inventory_repository.py
app/services/inventory_service.py
app/api/v1/schemas/inventory.py
app/api/v1/inventory.py
tests/test_inventory_api.py (10 testes)
```

### Backend — Timeline (W9)
```
app/domain/timeline/{entity.py, repository.py}
app/db/models/timeline_event.py
app/repositories/timeline_repository.py
app/services/timeline_service.py
app/api/v1/schemas/timeline.py
app/api/v1/timeline.py
tests/test_timeline_api.py (9 testes, incluindo 6 de integração cruzada)
```

### Migração
```
alembic/versions/c3d5f6560254_create_documents_inventory_timeline_.py
```

### Frontend
```
types/{document,inventory,timeline}.ts
lib/api/{documents,inventory,timeline}.ts
components/features/documents/{document-card,document-form}.tsx
components/features/inventory/{inventory-card,inventory-form}.tsx
components/features/timeline/timeline-item.tsx
app/(dashboard)/documents/page.tsx   — substitui o placeholder
app/(dashboard)/inventory/page.tsx   — substitui o placeholder
app/(dashboard)/timeline/page.tsx    — substitui o placeholder
```

### Documentação
```
docs/phases/PHASE_W7_W8_W9_REPORT.md — este ficheiro
docs/phases/screenshots-w7-w8-w9/*.png — 6 screenshots reais
```

---

## 4. Ficheiros modificados

- `backend/alembic/env.py` — adicionados imports de `DocumentModel`, `InventoryItemModel`, `TimelineEventModel`
- `backend/app/api/v1/router.py` — registados os três novos routers
- `backend/app/api/v1/memory.py` — endpoint `create_memory` agora também regista `MEMORY_CREATED` na Timeline (única alteração; `memory_service.py` não foi tocado)
- `backend/app/api/v1/tasks.py` — endpoints `create_task` e `update_task_status` agora também registam `TASK_CREATED`/`TASK_COMPLETED` (única alteração; `task_service.py` não foi tocado)

**Confirmado por `grep`:** nenhuma linha de `memory_service.py` ou `task_service.py` foi alterada nesta fase.

---

## 5. Base de dados — alterações

Três tabelas novas, todas aplicadas à base de dados real via Alembic:

```
documents         — title, description, category, file_name, file_type, file_size,
                     storage_path, tags[], expiry_date, tsvector+GIN, AuditMixin (soft delete)

inventory_items    — name, description, category, location, quantity, purchase_date,
                     purchase_price, serial_number, document_id (FK -> documents.id,
                     ON DELETE SET NULL), tsvector+GIN, AuditMixin (soft delete)

timeline_events    — event_type (enum), entity_type, entity_id, title, occurred_at,
                     created_at, tsvector+GIN — SEM soft delete (log apenas de acrescento)
```

Confirmado via `psql -d nexus -c '\dt'` e `\d inventory_items` (FK visível e correta) nesta sessão.

**Correção aplicada à migração antes de a aplicar** (mesma lição da W6): o `downgrade()` autogerado não removia o tipo `ENUM` `timeline_event_type` — corrigido manualmente antes de correr `alembic upgrade head`.

---

## 6. Endpoints da API

```
Documents:  POST/GET/PUT/DELETE /api/v1/documents, /{id}, GET /search
Inventory:  POST/GET/PUT/DELETE /api/v1/inventory, /{id}, GET /search
Timeline:   GET /api/v1/timeline (filtros: event_type, start_date, end_date),
            GET /api/v1/timeline/search
```

---

## 7. Limitação explícita — armazenamento de ficheiros (W7)

Conforme instruído, **não foi implementado upload real nem cloud storage**. `storage_path` é uma string livre fornecida pelo utilizador (ex.: um caminho local). NEXUS:
- **não** faz upload de ficheiros
- **não** lê o conteúdo do ficheiro
- **não** serve/descarrega o ficheiro
- **não** valida que o caminho existe

Testado explicitamente (`test_storage_path_is_metadata_only`): um caminho inexistente é aceite e guardado tal como foi enviado, sem qualquer tentativa de o validar contra um sistema de ficheiros.

---

## 8. Verificação executada (real, não assumida)

### 8.1 Testes automatizados — `uv run pytest -v`, 52 testes, contra PostgreSQL real

```
tests/test_document_api.py — 8 testes, todos PASSED
tests/test_inventory_api.py — 10 testes, todos PASSED (inclui referência a documento válida/inválida)
tests/test_memory_api.py — 7 testes, todos PASSED, sem regressão
tests/test_task_api.py — 15 testes, todos PASSED, sem regressão
tests/test_timeline_api.py — 9 testes, todos PASSED, incluindo:
  - cada módulo gera o evento certo na criação
  - conclusão de tarefa gera TASK_COMPLETED
  - uma tarefa criada+concluída gera exatamente 2 eventos distintos, não 1
  - atualização de inventário gera INVENTORY_UPDATED
  - ordenação por mais recente primeiro
  - pesquisa por texto

======================== 52 passed, 1 warning in 10.32s ========================
```

(warning é a mesma depreciação inofensiva já conhecida)

### 8.2 Verificação end-to-end no browser (Playwright, stack completa a correr)

Um bug real de configuração de teste foi encontrado e corrigido durante esta verificação (não um bug de produto — ver secção 10, item 1). Depois de corrigido, o fluxo completo foi confirmado com screenshots reais:
1. Documents vazio
2. Documento "Passport" criado (categoria, caminho de ficheiro, tudo visível)
3. Item de Inventory "Passport (physical)" criado e **ligado ao documento**, badge de link visível
4. Timeline agregando memórias, tarefas, documentos e inventário de todas as fases anteriores, mais recente primeiro
5. Timeline filtrada por `DOCUMENT_CREATED` — só documentos aparecem
6. Modo escuro confirmado (mesmo componente `ThemeToggle` já verificado em W4.5)

Todos os screenshots em `docs/phases/screenshots-w7-w8-w9/`.

### 8.3 Lint e build

```
frontend: pnpm lint  → 0 erros
frontend: pnpm build → sucesso, TypeScript ok, 8 rotas (Documents/Inventory/Timeline agora reais)
```

---

## 9. Revisão estática — fronteiras de dependência

- `domain/documents`, `domain/inventory`, `domain/timeline` — confirmado por `grep`: zero imports de infraestrutura
- `api/v1/{documents,inventory,timeline}.py` — confirmado por `grep`: só importam `services`, `schemas`, `domain`
- Nenhum `fetch()` fora de `lib/api/` no frontend — confirmado por `grep`
- Soft delete confirmado em Documents e Inventory (testes `test_delete_*_then_404`); Timeline é intencionalmente apenas de acrescento (sem soft delete — não há "eliminar" um evento)
- **Timeline recebe eventos de todos os quatro módulos** — confirmado pelos 6 testes de integração da secção 8.1, não apenas assumido

---

## 10. Problemas conhecidos

1. **Bug real de configuração encontrado durante a verificação E2E** (não um bug de produto): o último `pnpm build` desta sessão tinha sido feito sem `NEXT_PUBLIC_API_BASE_URL` definida, pelo que usou o fallback fixado no código para o backend de produção do Railway (definido numa fase de deployment anterior). Isto fez com que o browser tentasse contactar `backend-production-c978.up.railway.app` — inacessível a partir desta sandbox — em vez do backend local, resultando em erros "Failed to fetch". Diagnosticado por comparação direta com `curl` (que funcionou perfeitamente contra o backend local), corrigido reconstruindo com a variável de ambiente correta, e re-verificado com sucesso total.
2. **Sem upload real de ficheiros** — ver secção 7, limitação explícita e intencional desta fase.
3. **Sem paginação na UI** de nenhum dos três novos módulos — mesmo padrão já conhecido de Memory/Tasks.
4. **Tipos do frontend mantidos manualmente em sincronia** com os schemas Pydantic — mesmo padrão já conhecido.
5. **GitHub push continua pendente** — não resolvido nesta fase.

---

## 11. Build status

✅ **Build de frontend bem-sucedido**, ✅ **52/52 testes de backend a passar**, todos executados nesta sessão contra PostgreSQL real. Nenhuma alegação de sucesso não verificada.

---

## 12. Impacto no deployment de produção

**Nenhum, para já.** O backend em produção no Railway (`backend-production-c978.up.railway.app`) e o frontend no Vercel continuam a servir apenas W4.5+W6 (Memory+Tasks) — porque:
- O Railway faz deploy a partir do repositório GitHub `CletoPedro/Nexus-Web`, e este trabalho (W7-W9) ainda não foi commitado/pushed para lá
- O deploy do Vercel foi feito por envio direto de ficheiros (não ligado ao Git), pelo que também não reflete este trabalho automaticamente

Para este trabalho chegar a produção, é necessário: (a) resolver o push para o GitHub (decisão tua pendente desde há várias fases), e depois (b) fazer redeploy do backend no Railway (automático assim que o push acontecer, já que o serviço está ligado ao repositório) e (c) um novo `deploy_to_vercel` do frontend atualizado (ou ligar a GitHub App do Vercel para automatizar isto no futuro).

---

## 13. Próxima fase recomendada

- **Resolver o push para o GitHub**, para este trabalho poder chegar a produção
- **W10 — Universal Search** (agregando Memory, Tasks, Documents, Inventory), seguindo o roadmap original
- Ou reforçar qualidade: testes automatizados de frontend, autenticação básica

Aguardo a tua decisão antes de avançar. Não iniciei W10 nem toquei em nada fora do escopo definido (sem IA, sem NexusBrain, sem notificações, sem sincronização de calendário, sem cloud storage).
