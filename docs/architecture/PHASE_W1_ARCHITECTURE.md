# NEXUS WEB — PHASE W1: Web Architecture

**Status:** Proposta para aprovação — nenhuma implementação foi escrita nesta fase.
**Precedência:** Este documento é a fonte de verdade arquitetural para todas as fases W2+ até ser explicitamente revisto (equivalente a uma futura "Phase W1.1", seguindo o mesmo padrão usado no Android).
**Herança:** Reaproveita os conceitos validados nas Phases 1 / 2 / 2.1 do Android (domain contracts, repository pattern, conceitos de Memory, conceitos de NexusBrain, estratégia de abstração de IA, fronteiras de dependência), adaptados a uma stack Next.js + FastAPI + PostgreSQL.

---

## 1. Princípios Arquiteturais (herdados + adaptados)

1. **Separação de domínio e infraestrutura.** A lógica de domínio (entidades, regras, contratos) não depende de frameworks web, ORM ou fornecedores de IA.
2. **Sem vendor lock-in de IA.** Claude, OpenAI, Gemini e modelos locais são implementações substituíveis de uma interface `AIProvider`. Nenhuma camada de domínio ou de memória depende diretamente do SDK de um fornecedor.
3. **Memory é a camada de inteligência, não de persistência.** Tal como no Android, a persistência bruta (Postgres) é uma preocupação de infraestrutura; a camada Memory interpreta, indexa e recupera — não é apenas uma tabela.
4. **Sem implementações falsas.** Interfaces podem existir como placeholders explícitos (`NotImplementedError` documentado), mas nunca como lógica simulada que aparenta funcionar.
5. **Fronteiras de dependência explícitas e verificáveis.** Cada camada declara o que pode importar. Violações são bloqueantes, corrigidas em sub-fases dedicadas (ex.: W1.1), tal como aconteceu na Phase 2.1 do Android.
6. **Offline-first fica em standby, não abandonado.** A versão Web assume conectividade permanente por agora; o contrato de domínio é desenhado para não impedir uma futura estratégia offline/sync quando o cliente Android for retomado.

---

## 2. Estrutura do Repositório

```
nexus-web/
├── frontend/                  # Next.js (App Router) + TypeScript
├── backend/                   # FastAPI + Python
├── docs/                      # Documentação viva do projeto (este ficheiro entra aqui)
│   ├── architecture/
│   ├── phases/
│   └── decisions/              # ADRs (Architecture Decision Records)
├── infrastructure/            # IaC, docker-compose, configs de deployment
│   ├── docker/
│   ├── postgres/
│   └── env/
└── README.md
```

### Regras de fronteira de repositório
- `frontend` nunca acede diretamente à base de dados nem a chaves de fornecedores de IA — fala apenas com `backend` via API HTTP contratada (OpenAPI).
- `backend` nunca contém lógica de apresentação.
- `infrastructure` não contém lógica de negócio — apenas configuração e orquestração.
- `docs` é a única fonte de verdade sobre decisões — nenhuma decisão arquitetural é considerada válida se não estiver documentada aqui.

---

## 3. Frontend Architecture (Next.js + TypeScript)

```
frontend/
├── app/                        # App Router
│   ├── (auth)/
│   ├── (dashboard)/
│   │   ├── memory/
│   │   ├── tasks/
│   │   ├── documents/
│   │   ├── inventory/
│   │   ├── timeline/
│   │   ├── search/
│   │   └── now/                # Feature "NOW" (Step 14)
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ui/                     # shadcn/ui primitives
│   ├── layout/                 # navigation shell, sidebar, topbar
│   └── features/               # componentes específicos de domínio
├── lib/
│   ├── api/                    # cliente HTTP tipado (gerado a partir do OpenAPI do backend)
│   ├── theme/                  # dark/light mode
│   └── utils/
├── hooks/
├── types/                      # tipos partilhados, espelhando os schemas Pydantic do backend
└── config/
```

### Decisões
- **App Router obrigatório** (não Pages Router) — alinhado com Server Components e streaming.
- **shadcn/ui** para consistência visual sem impor um design system pesado.
- **Tema dark/light** implementado via CSS variables + `next-themes`, sem lógica de negócio embutida em componentes de tema.
- **Camada `lib/api` é a única porta de saída para o backend.** Componentes nunca fazem `fetch` diretamente — isto espelha a regra do Android de que a UI nunca fala diretamente com Room.
- **Tipos gerados/sincronizados a partir do OpenAPI do FastAPI**, evitando duplicação manual de contratos (equivalente aos "domain contracts" do Android).

---

## 4. Backend Architecture (FastAPI + Python)

```
backend/
├── app/
│   ├── api/                    # routers HTTP (camada de apresentação da API)
│   │   └── v1/
│   │       ├── memory.py
│   │       ├── tasks.py
│   │       ├── documents.py
│   │       ├── inventory.py
│   │       ├── timeline.py
│   │       ├── search.py
│   │       └── now.py
│   ├── domain/                 # entidades, regras de negócio, contratos (equivalente a :domain no Android)
│   │   ├── memory/
│   │   ├── tasks/
│   │   ├── documents/
│   │   ├── inventory/
│   │   └── timeline/
│   ├── services/                # orquestração de casos de uso, chama repositories + domain
│   ├── repositories/            # implementações concretas de persistência (equivalente a :data)
│   ├── ai/                      # AIProvider + implementações (equivalente a :ai)
│   │   ├── provider.py          # interface AIProvider
│   │   ├── claude_provider.py
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   └── local_provider.py
│   ├── brain/                   # NexusBrain (equivalente conceptual ao :ai/NexusBrain do Android)
│   │   ├── intent_detection.py
│   │   ├── memory_retrieval.py
│   │   └── tool_selection.py
│   ├── memory_engine/            # camada de inteligência de memória (equivalente a :memory)
│   ├── tools/                    # ferramentas que o NexusBrain pode invocar (equivalente a :tools)
│   ├── security/                 # auth, autorização, segredos (equivalente a :security)
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   └── secrets.py
│   ├── core/                     # config, logging, error handling (equivalente a :core)
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── db/                       # SQLAlchemy engine/session, Alembic
│   └── main.py
├── alembic/
├── tests/
└── pyproject.toml
```

### Fronteiras de dependência (regra explícita, tal como no Android)
| Camada | Pode importar | Não pode importar |
|---|---|---|
| `api` | `services`, `core`, `security` | `repositories`, `db` diretamente |
| `services` | `domain`, `repositories`, `brain`, `memory_engine` | `api` |
| `domain` | nada de infraestrutura | `db`, `ai`, `api`, frameworks web |
| `repositories` | `domain`, `db` | `api`, `ai` |
| `ai` | `domain` (contratos) | `repositories`, `db` |
| `brain` | `domain`, `ai`, `memory_engine`, `tools` | `api`, `repositories` diretamente (passa por `services`) |
| `memory_engine` | `domain`, `repositories` (via interface) | `ai` diretamente para persistência |
| `security` | `core` | `domain`, `services` |

Esta tabela é o equivalente direto às regras de dependência entre módulos Gradle no Android, e será validada manualmente em cada revisão estática de fase.

### Decisões
- **Injeção de dependência via `Depends()` do FastAPI**, papel equivalente ao Hilt no Android.
- **Configuração centralizada em `core/config.py`** usando Pydantic Settings — nenhuma variável de ambiente é lida fora desta camada.
- **Logging estruturado** desde o início (STEP 3), não adicionado a posteriori.
- **Health endpoints (`/health`, `/health/db`, `/health/ai`)** fazem parte da fundação, não de uma fase futura.
- **Error handling centralizado** via exception handlers do FastAPI — erros de domínio são mapeados para respostas HTTP consistentes, nunca deixados a propagar como stack traces genéricos.

---

## 5. Database Architecture (PostgreSQL)

- **SQLAlchemy 2.0 (estilo declarativo moderno)** como ORM.
- **Alembic** para todas as migrações — nenhuma alteração de esquema é feita manualmente na base de dados.
- **Um schema por domínio lógico não é usado inicialmente**; começamos com um único schema `public` e tabelas bem nomeadas (`memories`, `tasks`, `documents`, `inventory_items`, `timeline_events`), reavaliando particionamento apenas se necessário.
- **Chaves primárias UUID** (não seriais incrementais), para evitar acoplamento a um único banco de dados e facilitar uma futura sincronização com o cliente Android offline-first.
- **Colunas de auditoria obrigatórias** em todas as tabelas: `created_at`, `updated_at`, `deleted_at` (soft delete) — decisão herdada da disciplina de dados do Android.
- **Índices de pesquisa full-text** (Postgres `tsvector`) na tabela `memories` desde a Phase W... (a definir na fase de implementação de Memory), para suportar Universal Search sem depender de IA.

---

## 6. Memory Architecture

Reafirma o princípio já estabelecido no Android: **Memory é uma camada de inteligência, não uma tabela**.

```
Domain layer:      Memory (entidade), MemoryRepository (interface)
Repository layer:  PostgresMemoryRepository (implementação SQLAlchemy)
Memory Engine:      - indexação (tags, metadata, full-text)
                     - recuperação por relevância (não apenas por ID)
                     - expiração (expiresAt) e ciclo de vida
                     - futura ligação a embeddings (fora do escopo da W1)
```

- O CRUD puro de memórias (Step 5 do plano geral) deve funcionar **sem qualquer IA envolvida** — isto é um requisito arquitetural, não apenas funcional: prova que a camada de domínio não depende de `ai/`.
- O `NexusBrain` consulta a Memory Engine através de uma interface (`MemoryRetrieval`), nunca acedendo diretamente ao repositório Postgres.

---

## 7. NexusBrain Architecture

```
NexusBrain
├── IntentDetection     — interpreta a mensagem do utilizador em uma intenção estruturada
├── MemoryRetrieval      — pergunta à Memory Engine o contexto relevante
├── ToolSelection        — decide que ferramenta(s) de tools/ invocar
└── ResponseComposition  — usa AIProvider apenas na fase final de composição de linguagem
```

- **Claude (ou qualquer AIProvider) é usado apenas na fronteira de linguagem/raciocínio final** — nunca como substituto da lógica de intent detection determinística sempre que essa lógica for suficiente. Isto operacionaliza a regra do documento de execução: *"Claude is only one component."*
- **NexusBrain é modular por desenho**: cada submódulo (`intent_detection`, `memory_retrieval`, `tool_selection`) é testável isoladamente, sem precisar de uma chave de API de IA.
- Esta arquitetura só será implementada no Step 11 do plano geral (fase W muito posterior); aqui apenas se fixa o contrato.

---

## 8. Tool Architecture

- `tools/` define uma interface `Tool` (nome, descrição, schema de input, `execute()`).
- Ferramentas concretas (ex.: pesquisa de inventário, criação de tarefa) implementam esta interface e são registadas num `ToolRegistry`.
- O `NexusBrain.ToolSelection` escolhe ferramentas do registo — nunca chama serviços diretamente por nome fixo, para manter extensibilidade.
- Este desenho espelha deliberadamente o padrão de "tools" já usado nas interfaces placeholder do módulo `:tools` do Android.

---

## 9. Security Architecture

- **Autenticação:** JWT (access + refresh token), emitido pelo backend.
- **Autorização:** dependências FastAPI (`Depends(get_current_user)`) aplicadas por router, nunca verificada manualmente dentro de handlers individuais.
- **Segredos:** nunca em código nem em `docs/`; geridos via variáveis de ambiente e carregados só em `core/config.py` / `security/secrets.py`.
- **Chaves de fornecedores de IA:** armazenadas apenas no backend; o frontend nunca tem acesso direto a nenhuma chave de API de IA.
- **CORS:** restrito explicitamente às origens do frontend conhecido, nunca `*` em produção.
- **Rate limiting** nos endpoints de IA (Steps 11–14), para conter custos e abuso — a decidir a política exata na fase correspondente.

---

## 10. Roadmap (Web Phases)

O plano de 14 steps do documento de execução mantém-se como **roteiro de produto**, mas passa a ser entregue como **fases arquiteturais geridas**, seguindo exatamente a metodologia já usada no Android (arquitetura → implementação → revisão → verificação → relatório → aprovação):

| Fase | Conteúdo | Corresponde a |
|---|---|---|
| **W1** | Arquitetura completa (este documento) | — |
| **W2** | Repository scaffolding + fundação do frontend Next.js | Steps 1–2 |
| **W3** | Fundação do backend FastAPI (config, DI, logging, error handling, health) | Step 3 |
| **W4** | Persistência PostgreSQL (SQLAlchemy + Alembic) | Step 4 |
| **W5** | Memory Persistence (CRUD completo, sem IA) | Step 5 |
| **W6** | Tasks | Step 6 |
| **W7** | Documents | Step 7 |
| **W8** | Inventory | Step 8 |
| **W9** | Timeline | Step 9 |
| **W10** | Universal Search | Step 10 |
| **W11** | NexusBrain (intent detection, memory retrieval, tool selection) | Step 11 |
| **W12** | AI Provider abstraction | Step 12 |
| **W13** | Integração Claude | Step 13 |
| **W14** | Feature NOW | Step 14 |

Cada fase seguirá a estrutura já validada:
1. Explicação de design antes de qualquer código
2. Implementação estritamente limitada ao escopo da fase
3. Revisão estática de todos os ficheiros alterados
4. Checklist de verificação explícito
5. Relatório final (ficheiros criados/modificados, impacto arquitetural, impacto de dependências, testes executados, estado de build, problemas conhecidos, próxima fase)

**Nenhuma fase avança sem aprovação explícita.**

---

## 11. Nota sobre Verificação

Tal como no Android, este ambiente não tem acesso a Node.js/Python toolchains completos com todas as dependências de produção, nem a serviços externos (Postgres real, fornecedores de IA). Por isso:
- Nunca será declarado "build passou" ou "testes passaram" sem execução real e verificável.
- A revisão estática (leitura cuidadosa de código, verificação de imports e fronteiras de dependência) continua a ser o método de verificação por defeito, sempre explicitamente identificado como tal nos relatórios.
- Sempre que for possível executar algo real neste ambiente (ex.: `npm install`, `pip install`, linting, testes unitários sem dependências externas), isso será feito e reportado com o resultado exato.

---

## 12. Itens em Aberto para Aprovação

Antes de avançar para a **PHASE W2**, preciso da tua confirmação sobre:

1. **Nome do repositório / organização de pastas** — `nexus-web/` como raiz está correto, ou preferes outro nome?
2. **Gestor de pacotes do frontend** — `npm`, `pnpm` ou `yarn`?
3. **Gestor de pacotes/ambiente do backend** — `pip` + `venv`, `poetry`, ou `uv`?
4. **Autenticação:** para a W1 assumi JWT simples com um único utilizador (uso pessoal). Confirmas que não é necessário multi-tenant/multi-utilizador nesta fase do produto?
5. **Deployment alvo** (mesmo que não seja implementado já) — Docker Compose auto-hospedado, Vercel + serviço gerido de Postgres, ou outro? Isto influencia decisões em `infrastructure/`.

Aguardo aprovação (com ou sem ajustes aos pontos acima) antes de iniciar a **PHASE W2 — Repository Scaffolding + Frontend Foundation**.

---

## 13. Adenda — Estado real após W12 (atualizado)

Este documento mantém-se como referência arquitetural original. Alterações reais confirmadas desde então:

- **Autenticação implementada na W12** conforme previsto no ponto 4 acima: JWT single-user, arquitetura pronta para multi-utilizador (tabela `users`, `user_id` em todas as entidades de dados).
- **Deployment real:** Railway (backend + PostgreSQL) e Vercel (frontend), conforme o ponto 5. Estado atual detalhado, incluindo problemas de configuração encontrados e por resolver, em `docs/phases/PHASE_W12_REPORT.md`, secções 11-12.
- **Módulos implementados até à data:** Memory (W4.5), Tasks (W6), Documents/Inventory/Timeline (W7-W9), Global Search (W10), NOW Dashboard (W11), Security Foundation (W12). Ver `docs/phases/` para o relatório de cada fase.
- **GitHub:** o repositório `CletoPedro/Nexus-Web` está, à data deste documento, atrasado face a esta sandbox — contém até W7-W9. W10-W12 aguardam push manual (sem credenciais de escrita disponíveis ao agente).

