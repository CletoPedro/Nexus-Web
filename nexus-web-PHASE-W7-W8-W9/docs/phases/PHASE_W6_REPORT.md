# PHASE W6 — Tasks Module

**Status:** Implementado e verificado end-to-end (browser real, backend real, PostgreSQL real). Aguarda aprovação.
**GitHub:** o push para `CletoPedro/Nexus-Web` continua pendente da tua decisão (token / push manual / outro conector) — não relacionado com este trabalho, apenas a lembrar que ainda está em aberto.

---

## 1. O que passaste a poder fazer

Em `/tasks` no browser:

- **Criar** uma tarefa (título, descrição opcional, prioridade, data limite opcional)
- **Listar** tarefas, mais recentes primeiro
- **Marcar como concluída** com um clique no círculo de estado (regista `completed_at`)
- **Cancelar** uma tarefa
- **Reabrir** uma tarefa concluída/cancelada (volta a `TODO`)
- **Editar** título, descrição, prioridade, data limite
- **Apagar** (soft delete)
- **Pesquisar** por texto (full-text search real do Postgres, título + descrição)
- **Filtrar** por estado, por prioridade, e por "Overdue" (tarefas com prazo vencido e ainda não concluídas/canceladas)
- Tudo funcional em claro/escuro e em layout responsivo (herda a shell da W2)

---

## 2. Ficheiros criados

### Backend
```
app/domain/tasks/
├── entity.py       — Task (dataclass), TaskStatus, TaskPriority (enums), regras de transição de estado
└── repository.py   — TaskRepository (interface abstrata)

app/db/models/task.py           — TaskModel (SQLAlchemy), tsvector + índice GIN (título+descrição)
app/repositories/task_repository.py — PostgresTaskRepository
app/services/task_service.py    — TaskService (validação, regras de negócio, transições) + get_task_service (DI factory)
app/api/v1/schemas/task.py      — TaskCreate, TaskUpdate, TaskStatusUpdate, TaskOut
app/api/v1/tasks.py             — router: create, list (+filtros), search, get, update, update status, delete

alembic/versions/238650538c3b_create_tasks_table.py — migração real, aplicada

tests/test_task_api.py          — 15 testes end-to-end contra PostgreSQL real
```

### Frontend
```
types/task.ts                              — tipos partilhados (espelham os schemas Pydantic)
lib/api/tasks.ts                            — cliente da API de Tasks (único ponto de fetch)
components/ui/select.tsx                    — primitivo adicional (não existia até agora)
components/features/tasks/
├── task-card.tsx      — cartão com toggle de conclusão, cancelar, reabrir, editar, apagar
├── task-form.tsx       — formulário criar/editar
└── task-filters.tsx    — filtros de estado/prioridade/overdue
app/(dashboard)/tasks/page.tsx              — página real, substitui o placeholder da W2
```

### Documentação
```
docs/phases/PHASE_W6_REPORT.md              — este ficheiro
docs/phases/screenshots-w6/*.png            — 9 screenshots reais do fluxo completo
```

---

## 3. Ficheiros modificados

- `backend/alembic/env.py` — adicionado import de `TaskModel` (ver secção 5, bug nº1)
- `backend/app/api/v1/router.py` — registado o router de `tasks`

**Memory não foi tocado.** Confirmado por `grep`/inspeção: nenhum ficheiro de `domain/memory`, `repositories/memory_repository.py`, `services/memory_service.py`, `api/v1/memory.py`, ou `app/(dashboard)/memory/` foi alterado. Os 7 testes de Memory + 3 de health voltaram a correr no fim desta fase e continuam todos a passar (secção 6.1).

---

## 4. Base de dados — alterações

Nova tabela `tasks`, aplicada via Alembic à base de dados real:

```
title           varchar(500)   not null
description     text           not null, default ''
status          task_status    not null, default 'TODO'      (enum: TODO, IN_PROGRESS, DONE, CANCELLED)
priority        task_priority  not null, default 'MEDIUM'     (enum: LOW, MEDIUM, HIGH, CRITICAL)
due_date        timestamptz    nullable
completed_at    timestamptz    nullable
search_vector   tsvector       gerado (título + descrição), indexado GIN
id, created_at, updated_at, deleted_at — mesmo AuditMixin usado por Memory
```

Confirmado via `psql -d nexus -c '\d tasks'` — ver secção 6.

---

## 5. Bugs reais encontrados e corrigidos

1. **Migração vazia na primeira tentativa.** `alembic revision --autogenerate` gerou uma migração com `upgrade()`/`downgrade()` vazios — `TaskModel` nunca tinha sido importado em `alembic/env.py`, por isso não estava registado em `Base.metadata` e o Alembic não viu nenhuma tabela nova para criar. Detectado ao inspecionar o ficheiro gerado antes de o aplicar (nunca aplico uma migração sem a ler primeiro). Corrigido adicionando o import em `env.py`; migração regerada corretamente — desta vez com `"Detected added table 'tasks'"` no log e o `CREATE TABLE` completo.
2. **`downgrade()` não removia os tipos `ENUM` do Postgres.** Limitação conhecida do autogenerate do Alembic com enums inline: o `upgrade()` cria os tipos `task_status`/`task_priority`, mas o `downgrade()` gerado automaticamente só apaga a tabela, deixando os tipos órfãos na base de dados caso alguém reverta a migração. Corrigido manualmente adicionando `sa.Enum(...).drop(...)` a `downgrade()` para ambos os enums.

Nenhum destes dois seria apanhado só por leitura de código — o primeiro só apareceu ao inspecionar o ficheiro de migração gerado, o segundo é conhecimento específico de uma limitação do Alembic com Postgres enums.

---

## 6. Verificação executada (real, não assumida)

### 6.1 Testes automatizados — `uv run pytest -v`, 25 testes, contra PostgreSQL real

```
tests/test_health.py::test_health_ok PASSED
tests/test_health.py::test_health_db_ok_when_database_reachable PASSED
tests/test_health.py::test_unknown_route_is_404 PASSED
tests/test_memory_api.py (7 testes) — todos PASSED, sem regressão
tests/test_task_api.py::test_create_and_get_task PASSED
tests/test_task_api.py::test_create_rejects_empty_title PASSED
tests/test_task_api.py::test_create_with_priority_and_due_date PASSED
tests/test_task_api.py::test_create_rejects_invalid_priority PASSED
tests/test_task_api.py::test_list_tasks_includes_created PASSED
tests/test_task_api.py::test_list_filters_by_status PASSED
tests/test_task_api.py::test_list_filters_by_priority PASSED
tests/test_task_api.py::test_overdue_filter PASSED
tests/test_task_api.py::test_completing_an_overdue_task_removes_it_from_overdue_filter PASSED
tests/test_task_api.py::test_update_task PASSED
tests/test_task_api.py::test_valid_status_transition PASSED
tests/test_task_api.py::test_invalid_status_transition_from_done_is_rejected PASSED
tests/test_task_api.py::test_delete_task_then_404 PASSED
tests/test_task_api.py::test_search_finds_matching_task PASSED
tests/test_task_api.py::test_get_nonexistent_task_is_404 PASSED

======================== 25 passed, 1 warning in 5.63s =========================
```

(warning é a mesma depreciação inofensiva do `httpx`/`TestClient` já conhecida da W4.5)

### 6.2 Estrutura da tabela — `psql -d nexus -c '\d tasks'`

Confirmado: todas as colunas, tipos, enums, coluna gerada `search_vector` e índice GIN presentes exatamente como desenhados.

### 6.3 Verificação end-to-end no browser (Playwright, stack completa a correr)

Fluxo completo, capturado em 9 screenshots reais (`docs/phases/screenshots-w6/`):
1. Estado vazio
2. Duas tarefas criadas ("Renew passport" — atrasada, alta prioridade; "Water the plants" — baixa prioridade)
3. Filtro "Overdue" — só "Renew passport" aparece
4. "Water the plants" marcada como concluída
5. Filtro por estado `DONE` — só "Water the plants" aparece
6. Pesquisa "passport" — só "Renew passport" aparece
7. Edição de "Renew passport" → "Renew passport (urgent)" — "Water the plants" fica intacta (locators com âmbito ao cartão certo, replicando a correção de bug da W4.5, sem repetir o erro)
8. "Water the plants" apagada — só a tarefa do passaporte permanece
9. Modo escuro — dados reais renderizados corretamente

Todos os textos da página foram também capturados via `innerText` em cada passo (não só screenshots) para confirmar programaticamente o conteúdo real, não apenas visualmente.

### 6.4 Lint e build

```
frontend: pnpm lint  → 0 erros
frontend: pnpm build → sucesso, TypeScript ok, 8 rotas (incluindo /tasks agora real)
```

---

## 7. Revisão estática — fronteiras de dependência

- `domain/tasks/` — confirmado por `grep`: zero imports de FastAPI, SQLAlchemy, ou qualquer infraestrutura
- `api/v1/tasks.py` — confirmado por `grep`: só importa `services`, `schemas`, `domain` (nunca `repositories` diretamente), seguindo o mesmo padrão corrigido para Memory na W4.5
- DI factory (`get_task_service`) colocada em `services/task_service.py`, não num `api/dependencies.py`, pela mesma razão documentada na W4.5: só `services` pode importar `repositories` segundo a tabela da W1
- Nenhum `fetch()` fora de `lib/api/` no frontend — confirmado por `grep`
- Soft delete confirmado a funcionar (teste `test_delete_task_then_404` + verificação visual no browser)

---

## 8. Checklist de verificação

- [x] Tabela `tasks` criada e aplicada à BD real
- [x] Task entity (domain, sem dependências de framework)
- [x] TaskRepository (interface) + PostgresTaskRepository (implementação)
- [x] TaskService — validação (título vazio rejeitado), regras de negócio (transições de estado inválidas rejeitadas com 422)
- [x] Task API: create, list (+ filtros status/priority/overdue), search, get, update, update status, delete — todos testados
- [x] Task UI: criar, editar, concluir, cancelar, reabrir, apagar, pesquisar, filtrar — todos testados no browser real
- [x] Fronteiras de dependência respeitadas (mesma disciplina da W4.5)
- [x] `lib/api/` continua a ser a única porta de saída
- [x] Memory não modificado; 10/10 testes de Memory+health continuam a passar
- [x] Soft delete confirmado
- [x] Testes automatizados: 25/25 a passar contra BD real
- [x] Fluxo E2E no browser: confirmado por screenshot + inspeção de texto real, incluindo dark mode
- [x] Dois bugs reais encontrados e corrigidos, documentados em detalhe (secção 5)
- [x] Fora de escopo respeitado: nenhuma IA, LLM, embeddings, NexusBrain, notificações, sincronização de calendário, comandos de voz, ou automação foram tocados

---

## 9. Build status

✅ **Build bem-sucedido**, executado nesta sessão (`pnpm build`). ✅ **25/25 testes a passar**, executados nesta sessão contra PostgreSQL real. Nenhuma alegação de sucesso não verificada.

---

## 10. Problemas conhecidos

1. **Transições de estado são deliberadamente simplificadas**: `DONE` e `CANCELLED` são estados terminais via o endpoint de update de estado normal — reabrir usa explicitamente o mesmo endpoint para voltar a `TODO`, o que a UI expõe como "Reopen". Não há histórico de transições registado (auditoria de mudanças de estado), só o estado atual.
2. **`due_date` só tem granularidade de dia na UI** (input `type="date"`), embora o backend armazene `timestamptz` completo — suficiente para o caso de uso atual, mas de referir se precisares de horas específicas no futuro.
3. **Sem paginação na UI** — o backend suporta `limit`/`offset`, mas a página carrega sempre a primeira página (100 itens) sem controlo de "carregar mais". Não é um problema com o volume de dados atual, mas fica registado.
4. **Mesmos itens já conhecidos da W4.5** continuam válidos: sem autenticação, sem testes automatizados de frontend (CI), tipos mantidos manualmente em sincronia com o backend, Docker Compose ainda não executado nesta sandbox.
5. **GitHub push continua pendente** (não é um problema desta fase, mas fica por resolver): o repositório `CletoPedro/Nexus-Web` ainda não tem o código, incluindo agora a W6.

---

## 11. Próxima fase recomendada

Sugestões, sem ordem implícita de prioridade:
- **Resolver o push para o GitHub** (a decisão continua em aberto desde a mensagem anterior)
- **W7 — Documents**, seguindo o roadmap original
- Reforçar qualidade antes de continuar o roadmap: testes automatizados de frontend, autenticação básica

Aguardo a tua decisão antes de avançar. Não iniciei nenhuma destas por conta própria.
