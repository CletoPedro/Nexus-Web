# PHASE W4.5 — First Usable NEXUS

**Status:** Implementado e verificado end-to-end (browser real, backend real, PostgreSQL real). Aguarda a tua aprovação.
**Escopo:** Fundação de backend (W3) + partes essenciais de W4 (PostgreSQL/Alembic) + W5 (Memory completo: entidade, repositório, serviço, API, UI). Sem IA, sem NexusBrain, sem Tasks — exatamente como pedido.

---

## 1. O que passaste a poder fazer

Com o servidor a correr, em `/memory` no browser consegues:

- **Criar** uma memória (ex.: "My passport is inside the safe.", com tags opcionais)
- **Listar** todas as memórias, ordenadas por mais recente
- **Pesquisar** por texto (full-text search real do Postgres — sem IA) — ex.: pesquisar "passport" encontra a memória certa e ignora as outras
- **Editar** uma memória existente
- **Apagar** uma memória (soft delete — fica marcada `deleted_at`, não é destruída fisicamente)
- **Alternar tema** claro/escuro, com os dados reais a renderizar corretamente em ambos

Este é o cenário exato descrito no documento original: "Remember that my passport is inside the safe" → mais tarde "Where is my passport?" → NEXUS encontra a resposta na sua própria camada de memória, sem qualquer IA envolvida.

---

## 2. Ficheiros criados

### Backend (`backend/`)
```
app/
├── core/
│   ├── config.py           — Settings centralizado (pydantic-settings)
│   ├── logging.py          — logging estruturado
│   └── exceptions.py       — NexusError, NotFoundError, ValidationError, ConflictError + handlers
├── api/
│   ├── health.py           — /health, /health/db (round-trip real à BD)
│   └── v1/
│       ├── router.py       — agrega routers de domínio
│       ├── memory.py       — endpoints REST de Memory
│       └── schemas/memory.py — MemoryCreate, MemoryUpdate, MemoryOut (Pydantic)
├── domain/
│   └── memory/
│       ├── entity.py       — Memory (dataclass, sem dependências de framework)
│       └── repository.py   — MemoryRepository (interface abstrata)
├── repositories/
│   └── memory_repository.py — PostgresMemoryRepository (implementação SQLAlchemy)
├── services/
│   └── memory_service.py   — MemoryService + get_memory_service (DI factory)
├── db/
│   ├── base.py              — Base declarativa + AuditMixin (id, created_at, updated_at, deleted_at)
│   ├── session.py           — engine assíncrono + get_db_session
│   └── models/memory.py     — MemoryModel (SQLAlchemy), com tsvector + índice GIN
└── main.py                  — application factory

alembic/
├── env.py                   — configurado para ler Settings e o metadata dos nossos modelos
└── versions/7ba5622bf8d2_create_memories_table.py — primeira migração real, aplicada

tests/
├── test_health.py
└── test_memory_api.py       — 7 testes end-to-end contra PostgreSQL real

Dockerfile, .dockerignore, .env.example
```

### Frontend (`frontend/`)
```
lib/api/
├── client.ts                — cliente HTTP base (única porta de saída para o backend)
└── memory.ts                — funções da API de Memory

types/memory.ts               — tipos partilhados (espelham os schemas Pydantic)

components/
├── ui/{input,textarea}.tsx   — primitivos adicionais shadcn-style
└── features/memory/
    ├── memory-card.tsx       — cartão de memória (visual "ficha de arquivo")
    └── memory-form.tsx       — formulário de criar/editar

app/(dashboard)/memory/page.tsx — página real, substituindo o placeholder da W2

Dockerfile, .dockerignore, .env.local.example
```

### Infraestrutura
```
infrastructure/docker/docker-compose.yml — Postgres + backend + frontend
```

### Documentação
```
README.md                                  — instruções de execução local + Docker
docs/phases/PHASE_W4_5_REPORT.md           — este ficheiro
docs/phases/screenshots-w4.5/*.png         — 7 screenshots reais do fluxo completo
```

---

## 3. Arquitetura — decisões e conformidade

- **Fronteiras de dependência da W1 respeitadas e re-verificadas.** Durante a revisão estática desta fase encontrei uma violação real: `api/v1/dependencies.py` importava `repositories` diretamente, o que a tabela da W1 não permite (`api` só pode importar `services`). Corrigi movendo a fábrica de DI (`get_memory_service`) para dentro de `services/memory_service.py`, que já tem permissão para importar `repositories`. Removido o ficheiro `dependencies.py`. Voltei a correr toda a suite de testes depois da correção — 10/10 continuam a passar.
- **Exceção documentada:** `api/health.py` importa `db.session` diretamente para o `/health/db`. Isto é uma checagem de infraestrutura pura (round-trip à BD), não um fluxo de domínio, por isso considero-a uma exceção aceitável à tabela — mas fica aqui registada, não silenciada.
- **`domain/memory/` não importa nada de infraestrutura** (nem SQLAlchemy, nem FastAPI) — confirmado por `grep`.
- **CRUD funciona sem IA** — arquitetural e literalmente: nenhum módulo de `ai/` ou `brain/` foi tocado nesta fase.
- **Full-text search real**: coluna `tsvector` gerada pelo Postgres (`GENERATED ALWAYS AS`) + índice GIN, consultada via `ts_rank`/`plainto_tsquery`. Não há nenhuma dependência de IA na pesquisa.
- **Soft delete**: `deleted_at` é definido, a linha nunca é apagada fisicamente; todas as queries filtram `deleted_at IS NULL`.

---

## 4. Desvios do plano (documentados)

| Desvio | Motivo | Impacto |
|---|---|---|
| `NullPool` em vez de pool de conexões normal no engine assíncrono | Erro real encontrado durante os testes: `"another operation is in progress"` — ligações `asyncpg` são vinculadas ao event loop onde foram criadas, e o `TestClient` cria um loop novo por pedido. `NullPool` abre uma ligação nova por checkout, trocando alguma latência por correção entre loops. | Nenhum impacto arquitetural; é uma decisão de configuração do engine, documentada no próprio código (`db/session.py`). Num ambiente de produção normal (sem `TestClient`), isto ainda é seguro, apenas ligeiramente menos eficiente que um pool persistente — pode ser revisto numa fase de otimização futura se necessário. |
| Composição de DI movida de `api/v1/dependencies.py` para `services/memory_service.py` | Violação de fronteira encontrada na revisão estática (secção 3) | Corrige a arquitetura para bater certo com a tabela da W1; sem perda de funcionalidade |
| Docker Compose escrito mas não executado nesta sandbox | Docker não está instalado neste ambiente de desenvolvimento, e os registos de imagens (Docker Hub, GHCR) não estão na lista de domínios permitidos | Documentado explicitamente no README como "revisto mas não verificado" — tudo o que o Compose orquestra foi verificado a correr diretamente no host (Postgres real, migração real, API real, frontend real). Pedido explícito: corre `docker compose up --build` no teu ambiente e reporta qualquer problema. |

---

## 5. Bugs reais encontrados e corrigidos durante a verificação

Dois bugs genuínos apareceram ao testar de verdade (não teria sido possível encontrá-los apenas por revisão estática):

1. **`asyncpg` + `TestClient`: "another operation is in progress".** 6 de 10 testes falhavam. Causa: ligações `asyncpg` presas ao event loop onde nasceram; `TestClient` recria o loop a cada pedido síncrono. Corrigido com `NullPool` (ver secção 4). Depois da correção: 10/10 testes a passar.
2. **Bug no meu próprio script de teste E2E** (não na aplicação): o primeiro script Playwright usava `.first()` para encontrar o botão "editar" depois de fazer hover num cartão específico — mas ambos os botões "editar" já existem no DOM (só ficam visualmente escondidos via CSS `opacity`), por isso `.first()` apanhava sempre o botão do primeiro cartão da lista, independentemente de qual tinha sido "hovered". Resultado: o teste editou a memória errada. Diagnosticado ao inspecionar o estado real da página (não assumido), corrigido ao usar um locator com âmbito ao cartão certo (`div.group` que contém aquele texto específico), e re-executado com sucesso. Fica registado porque é exatamente o tipo de coisa que a disciplina de "nunca assumir sucesso, verificar sempre" existe para apanhar.

---

## 6. Testes executados (reais, não assumidos)

### 6.1 Testes automatizados — `uv run pytest -v`, contra PostgreSQL real

```
collected 10 items

tests/test_health.py::test_health_ok PASSED                              [ 10%]
tests/test_health.py::test_health_db_ok_when_database_reachable PASSED   [ 20%]
tests/test_health.py::test_unknown_route_is_404 PASSED                   [ 30%]
tests/test_memory_api.py::test_create_and_get_memory PASSED              [ 40%]
tests/test_memory_api.py::test_create_rejects_empty_content PASSED       [ 50%]
tests/test_memory_api.py::test_list_memories_includes_created PASSED     [ 60%]
tests/test_memory_api.py::test_update_memory PASSED                      [ 70%]
tests/test_memory_api.py::test_delete_memory_then_404 PASSED             [ 80%]
tests/test_memory_api.py::test_search_finds_matching_memory PASSED       [ 90%]
tests/test_memory_api.py::test_get_nonexistent_memory_is_404 PASSED      [100%]

======================== 10 passed, 1 warning in 1.78s =========================
```

(o único warning é uma depreciação do `starlette.testclient` sobre `httpx`, sem impacto funcional)

### 6.2 Smoke test manual via `curl`, contra `uvicorn` real + Postgres real

Sequência completa executada e confirmada nesta sessão: `POST /memories` → `GET /memories/{id}` → `GET /memories` (lista) → `GET /memories/search?q=passport` (encontra) → `PUT /memories/{id}` (atualiza) → `DELETE /memories/{id}` → 204 → `GET /memories/{id}` → 404 → `GET /health/db` → `{"status":"ok"}`. Todos os passos confirmados com o JSON de resposta real.

### 6.3 Verificação end-to-end no browser (Playwright, contra a stack completa a correr)

Fluxo completo executado e capturado em screenshot real (não simulado):
1. Estado vazio (`docs/phases/screenshots-w4.5/01-empty-state.png`)
2. Criar a memória do passaporte (`02-creating-memory.png`)
3. Criar uma segunda memória (HDMI) — duas memórias na lista (`03-two-memories.png`)
4. Pesquisar "passport" — só a memória certa aparece (`04-search-results.png`)
5. Editar a memória do passaporte — conteúdo atualizado, a memória HDMI fica intacta (`05-after-edit.png`)
6. Apagar a memória HDMI — só a do passaporte permanece (`06-after-delete.png`)
7. Alternar para modo escuro — dados reais renderizados corretamente (`07-dark-mode.png`)

Todos os screenshots estão em `docs/phases/screenshots-w4.5/`.

### 6.4 Lint e build

```
frontend: pnpm lint  → 0 erros
frontend: pnpm build → sucesso, TypeScript ok, 8 rotas
```

---

## 7. Checklist de verificação

- [x] PostgreSQL real instalado, a correr, com dados persistentes entre reinícios
- [x] Alembic configurado contra o `Settings` da app; migração gerada a partir dos modelos reais
- [x] Migração aplicada à base de dados real; tabela `memories` confirmada via `psql \d`
- [x] Memory entity (domain, sem dependências de framework)
- [x] MemoryRepository (interface) + PostgresMemoryRepository (implementação)
- [x] MemoryService (validação + orquestração)
- [x] Memory API: create, get, list, update, delete, search — todos testados
- [x] Memory UI: criar, editar, apagar, listar, pesquisar — todos testados no browser real
- [x] CRUD funciona sem qualquer módulo de IA tocado
- [x] Fronteiras de dependência re-verificadas; uma violação real encontrada e corrigida
- [x] `lib/api/` continua a ser a única porta de saída do frontend
- [x] Testes automatizados: 10/10 a passar contra BD real
- [x] Smoke test manual via `curl`: todos os endpoints confirmados
- [x] Fluxo E2E no browser: confirmado por screenshot real, incluindo dark mode
- [x] Dockerfiles + docker-compose.yml escritos e revistos
- [ ] Docker Compose executado de facto — **não verificável nesta sandbox** (ver secção 4); pedido explícito para testares no teu ambiente
- [x] Instruções de execução local (sem Docker) escritas e conferidas passo a passo contra o que foi realmente executado

---

## 8. Problemas conhecidos

1. **Docker Compose não foi executado nesta sandbox** (sem Docker instalado, sem acesso a Docker Hub/GHCR). Todo o código individual que ele orquestra foi verificado a correr fora de containers. Pede-se verificação no teu ambiente.
2. **Tipos do frontend (`types/memory.ts`) são mantidos manualmente em sincronia** com os schemas Pydantic do backend, não gerados automaticamente a partir do OpenAPI. Referido como melhoria candidata para uma fase futura (a W1 já previa isto na secção 3 do documento de arquitetura).
3. **`NullPool` no engine assíncrono** troca alguma eficiência de conexão por correção entre event loops (ver secção 4) — aceitável para este estágio de single-user, pode ser revisto se a carga aumentar.
4. **Sem autenticação ainda.** A API de Memory está completamente aberta (sem JWT) — isto está alinhado com o roadmap (Security é uma fase própria, ainda não alcançada) mas significa que, tal como está, não deve ser exposta fora de `localhost`/rede de confiança.
5. **Sem testes automatizados no frontend** (Vitest/Playwright como suite CI) — a verificação desta fase foi manual mas real (screenshots + inspeção de estado), não uma suite reprodutível. Candidato para uma fase de qualidade futura.

---

## 9. Próxima fase proposta

Com Memory totalmente funcional, o roadmap original (W6 — Tasks) continua disponível, mas dado que pediste para otimizar por usabilidade antes, sugiro perguntar-te diretamente qual preferes a seguir:
- **W6 — Tasks** (seguir o roadmap original)
- Reforçar W4.5 primeiro (testes automatizados de frontend, autenticação básica, ou verificação real do Docker Compose no teu ambiente)

Aguardo a tua decisão antes de avançar.
