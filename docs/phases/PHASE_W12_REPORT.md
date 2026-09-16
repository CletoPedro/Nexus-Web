# PHASE W12 — Security Foundation

**Status:** Implementada e verificada end-to-end (backend real, PostgreSQL real, browser real). Fase crítica, tratada com o rigor pedido.

---

## 1. Decisões arquiteturais

### Autenticação: JWT em cookie httpOnly, não localStorage
Escolhi **tokens JWT stateless, transportados num cookie `httpOnly` + `Secure` + `SameSite`**, em vez de sessões server-side com tabela própria. Motivo: a stack já está distribuída (frontend no Vercel, backend no Railway — origens diferentes), e um cookie httpOnly é a única forma de manter o token completamente invisível ao JavaScript do browser, cumprindo à risca "NÃO colocar tokens em localStorage se existir alternativa segura".

`Secure` e `SameSite` são **condicionais ao ambiente** (`core/config.py`, `cookie_secure`/`cookie_samesite`): em produção, `Secure=true` + `SameSite=none` (necessário para cookies cross-site entre `vercel.app` e `railway.app`); em desenvolvimento local, `Secure=false` + `SameSite=lax` (um cookie `Secure` seria silenciosamente ignorado pelo browser em `http://localhost`, o que partiria o login local).

**Limitação documentada, não escondida:** por ser stateless, não há revogação server-side imediata — um "logout" limpa o cookie do lado do cliente, mas um token roubado antes disso continua válido até expirar (7 dias, configurável). Uma blocklist de tokens ou uma tabela de sessões resolveria isto numa fase de hardening futura; não foi implementada agora por ser explicitamente fora do escopo mínimo pedido ("OBJETIVO INICIAL: Single-user authentication").

### Sem endpoint de registo público
Só existem `/auth/login`, `/auth/logout`, `/auth/me` — não há `/auth/register`. Coerente com "single-user" e com não abrir uma porta de criação de contas não solicitada.

### Erros de login idênticos para "utilizador não existe" e "password errada"
Nunca se revela qual das duas coisas falhou — testado explicitamente.

### 404, nunca 403, em dados de outro utilizador
Quando o User B tenta aceder a um recurso do User A, a resposta é sempre 404, nunca 403 — para não revelar sequer que o recurso existe. Implementado ao nível do repositório: `get`/`update`/`delete` filtram por `id AND user_id` na mesma query.

---

## 2. Ficheiros criados

### Backend — Auth
```
domain/users/{entity.py, repository.py}
db/models/user.py
repositories/user_repository.py
security/{hashing.py, tokens.py, dependencies.py}
services/{user_service.py, auth_service.py}
api/v1/schemas/auth.py
api/v1/auth.py
```

### Migração
```
alembic/versions/a68b4885b8dc_add_users_table_and_user_id_ownership_.py
```

### Testes
```
tests/conftest.py — fixtures client/other_client/anon_client (autenticação real via /auth/login)
tests/test_auth_api.py — 8 testes
tests/test_protected_endpoints.py — 17 testes (parametrizados, um por endpoint de dados)
tests/test_ownership_isolation.py — 10 testes
```

### Frontend
```
types/auth.ts, lib/api/auth.ts
components/layout/{auth-guard.tsx, logout-button.tsx}
app/login/page.tsx
```

### Documentação
```
docs/phases/PHASE_W10_REPORT.md, PHASE_W11_REPORT.md, PHASE_W12_REPORT.md (este ficheiro)
docs/phases/screenshots-w12/*.png (8 screenshots reais)
```

---

## 3. Ficheiros modificados

**Todos os módulos de dados** (Memory, Tasks, Documents, Inventory, Timeline) tiveram as suas entidades de domínio, modelos ORM, repositórios, serviços e routers atualizados para: adicionar `user_id`, filtrar todas as leituras/escritas por `user_id`, e proteger todos os endpoints com `Depends(get_current_user)`.

Especificamente: `domain/{memory,tasks,documents,inventory,timeline}/{entity,repository}.py`, `db/models/{memory,task,document,inventory_item,timeline_event}.py`, `repositories/{memory,task,document,inventory,timeline}_repository.py`, `services/{memory,task,document,inventory,timeline}_service.py`, `api/v1/{memory,tasks,documents,inventory,timeline}.py`, mais `services/search_service.py`, `api/v1/search.py`, `services/now_service.py`, `api/v1/now.py`.

`api/v1/router.py` — registado o router de auth. `alembic/env.py` — registado `UserModel`. `.env.example` (backend) — adicionadas `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_INITIAL_PASSWORD`, sem valores reais. `.gitignore` (backend) — reforçado para nunca commitar `.env`. `app/(dashboard)/layout.tsx` — envolvido em `<AuthGuard>`. `components/layout/app-shell.tsx` — adicionado botão de logout.

**Confirmado por execução real dos 104 testes:** nenhuma regressão nos módulos pré-existentes apesar da reescrita extensa.

---

## 4. Base de dados — migração

Tabela `users` criada (email único, password com hash bcrypt, `is_active`, `must_change_password`). Coluna `user_id` (FK para `users.id`, `ON DELETE CASCADE`, nome de constraint explícito) adicionada a `memories`, `tasks`, `documents`, `inventory_items`, `timeline_events`.

**Bootstrap admin condicional, nunca hardcoded:** a migração lê `ADMIN_EMAIL`/`ADMIN_INITIAL_PASSWORD` do ambiente. Se ambas estiverem definidas: cria o utilizador (`must_change_password=true`), faz backfill de todas as linhas pré-existentes, e só depois torna `user_id` `NOT NULL`. **Se não estiverem definidas: a migração ainda corre, adiciona as colunas, mas fica tudo nullable e nenhum dado pré-existente é atribuído a ninguém** — documentado explicitamente, nunca escondido.

Testado localmente com `ADMIN_EMAIL=pedro@example.com ADMIN_INITIAL_PASSWORD=ChangeMe123!Bootstrap` — confirmado via `psql`: FK nomeada corretamente, `NOT NULL` aplicado, 137 linhas de memórias de teste (acumuladas de fases anteriores) herdadas com sucesso pelo admin.

### Bug real encontrado e corrigido na migração
O autogenerate do Alembic produziu `op.drop_constraint(None, ...)` no `downgrade()` — `None` não é um nome de constraint válido, o que faria o downgrade falhar sempre. Corrigido nomeando explicitamente cada FK (`fk_<tabela>_user_id_users`).

---

## 5. Endpoints da API

```
POST /api/v1/auth/login   — devolve o utilizador, define o cookie de sessão
POST /api/v1/auth/logout  — limpa o cookie
GET  /api/v1/auth/me      — utilizador atual (requer sessão)
```

Todos os endpoints de dados já existentes (Memory, Tasks, Documents, Inventory, Timeline, Search, Now) continuam com a mesma forma, mas agora **exigem sessão válida** e **filtram sempre pelo utilizador autenticado**.

---

## 6. Testes (35 novos + 69 pré-existentes atualizados = 104 no total)

### 6.1 Auth (8 testes)
Login correto; login com password errada; login com email inexistente (erro idêntico); `/me` sem sessão → 401; `/me` com sessão → dados corretos; logout limpa a sessão; cookie inválido rejeitado; **cookie adulterado rejeitado** (pega num token real e válido, corrompe os últimos 4 caracteres, confirma rejeição).

### 6.2 Endpoints protegidos (17 testes parametrizados)
Cada um dos 16 endpoints de dados testado individualmente sem sessão → 401. `/health` e `/health/db` confirmados como **continuando públicos** (necessário para os healthchecks do Railway).

### 6.3 Isolamento entre utilizadores (10 testes) — o requisito central desta fase
Dois utilizadores reais, independentemente autenticados. Confirmado: User B não consegue ler, listar, atualizar, nem apagar dados do User A (get→404, update→404 sem alterar nada, delete→sem efeito, list→nunca inclui); pesquisa nunca cruza utilizadores; isolamento confirmado nos 4 módulos de dados simultaneamente; **Inventory não pode ligar-se a um Document de outro utilizador** mesmo sendo um ID válido e existente; Timeline, NOW, e Global Search todos isolados por utilizador.

### 6.4 Execução real
```
uv run pytest -q
104 passed, 1 warning in ~18s
```

---

## 7. Verificação end-to-end no browser (real, não simulada)

Fluxo completo com Playwright contra o stack completo a correr:
1. Acesso direto a `/now` sem sessão → redireciona para `/login` ✅
2. Login com password errada → mensagem de erro, fica em `/login` ✅
3. Login correto → redireciona para `/now` ✅
4. Todas as páginas de módulo acessíveis autenticado, com dados reais herdados do bootstrap visíveis ✅
5. Pesquisa global funcional autenticado ✅
6. Mobile: dashboard completo, botão de logout visível ✅
7. Dark mode: confirmado autenticado ✅
8. Logout → redireciona para `/login` ✅
9. **Acesso direto a `/tasks` depois do logout → redireciona de novo para `/login`** ✅

Screenshots em `docs/phases/screenshots-w12/`.

### Bug real encontrado durante o E2E (script de teste, não a aplicação)
Um seletor ambíguo no meu próprio script Playwright clicou sem querer no trigger de pesquisa global antes de tentar alternar o tema, deixando o diálogo aberto a interceptar cliques seguintes. Diagnosticado pela mensagem de erro do Playwright, corrigido, re-executado com sucesso total.

---

## 8. Revisão de segurança (hardening)

- **CORS:** allowlist explícita — nunca `*`.
- **Cookies:** `httpOnly` sempre; `Secure`/`SameSite` condicionais ao ambiente.
- **Password hashing:** bcrypt, 12 rounds.
- **Expiração de token:** 7 dias (configurável).
- **Vazamento de erros da API:** confirmado que exceções não tratadas devolvem mensagem genérica, nunca stack trace.
- **Logging:** confirmado por `grep` que nenhuma password ou token passa por `print`/`logger`.
- **`.env.example`:** sem valores reais, placeholders explícitos com instruções.
- **`.gitignore`:** reforçado no backend para nunca commitar `.env`.
- **Frontend:** confirmado por `grep` que `localStorage`/`sessionStorage` não são usados em lado nenhum.

---

## 9. Revisão estática (arquitetura)

`domain/users/` sem dependências de infraestrutura. Todos os routers só importam `services`/`schemas`/`domain`/`security` (nunca `repositories` diretamente, exceto a exceção já documentada de `health.py`). Nenhum `fetch()` fora de `lib/api/`. Sem lógica fake/mock. Sem IA introduzida.

---

## 10. Lint, Build

```
frontend: pnpm lint  → 0 erros
frontend: pnpm build → sucesso, 12 rotas (incluindo /login)
```

---

## 11. Estado real do GitHub, Railway e Vercel (verificado, não assumido)

### GitHub
Confirmado via clone real: o repositório continua apenas com W7-W9 (commit `5e7c4f5`). **O trabalho de W10, W11 e W12 existe apenas nesta sandbox** — continuo sem credenciais de push.

### Railway
Confirmado via `list-deployments`: o backend em produção **nunca fez redeploy desde o commit inicial** (`0b8ae9b`) — nem sequer chegou a servir W7-W9.

### Vercel — problema real encontrado
A GitHub App do Vercel foi entretanto instalada e tentou fazer deploy automático a partir de dois pushes — **mas ambos falharam** (`state: ERROR`). Logs de build reais:

```
Error: Couldn't find any `pages` or `app` directory. Please create one under the project root
```

**Causa:** o projeto Vercel não tem "Root Directory" configurado para `frontend/`. **Não tenho ferramenta disponível para alterar esta definição num projeto já existente.** Precisa de correção manual: Vercel → projeto `nexus-web` → Settings → General → Root Directory → `frontend` → Save.

**Consequência prática:** o site público continua a servir o deploy direto original (W4.5+W6 apenas), sem Documents/Inventory/Timeline/Search/NOW/Login.

---

## 12. O que falta para isto chegar a produção

1. **Corrigir o Root Directory no Vercel** (secção 11).
2. **Push desta sandbox para o GitHub** — sem credenciais, falta correr:
   ```bash
   git add -A
   git commit -m "feat: implement Global Search, NOW Dashboard, and Security Foundation (W10-W12)"
   git push origin main
   ```
3. **Definir `SECRET_KEY` no Railway** (gerar com `python -c "import secrets; print(secrets.token_urlsafe(48))"`), e opcionalmente `ADMIN_EMAIL`/`ADMIN_INITIAL_PASSWORD`.
4. Confirmar redeploy automático do Railway após o push (não confirmado como funcional nas fases anteriores).
5. Confirmar redeploy automático do Vercel após o Root Directory corrigido.

---

## 13. Problemas conhecidos (resumo)

1. Sem revogação de sessão server-side imediata.
2. Sem `/auth/register` — só single-user via bootstrap, por desenho.
3. Bootstrap admin só corre se as env vars estiverem definidas no momento da migração.
4. **Vercel com Root Directory mal configurado** — precisa de correção manual.
5. **Railway nunca fez redeploy automático** desde o commit inicial.
6. GitHub continua sem W10-W12 — push pendente.
7. Sem testes automatizados de frontend em CI.

---

## 14. Próximo passo recomendado

Resolver os itens da secção 12; considerar CI/testes de frontend antes de continuar o roadmap (W13+, IA/NexusBrain, fora de escopo desta execução).
