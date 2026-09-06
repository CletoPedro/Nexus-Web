# PHASE W4.7A — Direct Public Deployment (Live)

**Status:** Backend e base de dados em produção, verificados via a própria plataforma Railway. Frontend em produção no Vercel, verificado por pedidos HTTP reais. Validação de CRUD ponta-a-ponta a partir de um browser real **não foi possível a partir desta sandbox** (ver secção de limitações) — pede-se confirmação final no teu telemóvel.

---

## URLs

| | URL |
|---|---|
| **Frontend** | https://nexus-web-the-mini-mialis.vercel.app |
| **Backend** | https://backend-production-c978.up.railway.app |
| **Health** | https://backend-production-c978.up.railway.app/health |
| **Health DB** | https://backend-production-c978.up.railway.app/health/db |
| **API docs** | https://backend-production-c978.up.railway.app/docs |

---

## O que foi feito nesta sessão

### Railway
1. Confirmado o repositório `CletoPedro/Nexus-Web` completo (W6 incluído), sem segredos.
2. Serviço `backend` criado a partir do repositório GitHub real (`Railway:create-deployment`).
3. **Bug real encontrado e corrigido**: o `startCommand` inicial não estava a ser interpretado por uma shell (`&&` e `$PORT` não eram expandidos), e o Python estava a bufferizar a saída, escondendo os logs reais. Corrigido com `sh -c "..."` explícito, `PYTHONUNBUFFERED=1`, e porta fixa (`8000`).
4. Migrações Alembic (`memories`, `tasks`) aplicadas automaticamente no arranque, confirmadas nos logs reais de produção.
5. Domínio público gerado; `CORS_ORIGINS` atualizado com o URL real do Vercel depois deste ficar disponível.

### Vercel
1. `create_git_project` falhou — a GitHub App do Vercel não está instalada nesta conta/repositório (exige autorização tua, não posso fazer por ti).
2. Usei `deploy_to_vercel` (envio direto de ficheiros) como alternativa — não depende da GitHub App.
3. `NEXT_PUBLIC_API_BASE_URL` foi fixado como fallback no código-fonte (`lib/api/client.ts`) para o URL real do backend, já que este método de deploy não suporta variáveis de ambiente.
4. Build real confirmado (`Vercel:get_deployment_build_logs`): compilação, type-check e as 8 rotas geradas com sucesso.
5. **Problema real encontrado e corrigido**: a proteção SSO do Vercel estava ativada por omissão em todos os deployments, o que teria bloqueado o acesso a partir do teu telemóvel com um ecrã de login da Vercel. Desativei (`ssoProtection: false`) — a app já não tem autenticação própria nesta fase, por isso isto não introduz uma exposição nova de dados sensíveis, apenas remove uma barreira de acesso involuntária.

---

## Verificação executada (real)

| Verificação | Método | Resultado |
|---|---|---|
| Backend healthcheck | Status da plataforma Railway (`get-status`) — só marca `SUCCESS` depois do próprio `/health` responder | ✅ SUCCESS |
| Backend logs de arranque | `Railway:get-logs` | ✅ `Uvicorn running on http://0.0.0.0:8000`, sem erros |
| Migrações aplicadas | Logs de deploy reais | ✅ `Running upgrade -> ... create memories table`, `... create tasks table` |
| Frontend build | `Vercel:get_deployment_build_logs` | ✅ compilação e build completos, 8 rotas |
| Frontend HTTP real | `Vercel:web_fetch_vercel_url` em `/memory` e `/tasks` | ✅ 200, HTML correto, nav completa, filtros de Tasks presentes |
| Proteção de acesso | `Vercel:get_project_deployment_protection` | ✅ confirmado e corrigido (SSO estava a bloquear acesso público) |

## Limitação honesta

**Não consegui validar o fluxo completo de CRUD (criar/editar/apagar Memory e Tasks) a partir de um browser real contra os URLs públicos.** Esta sandbox não tem acesso de rede a `*.railway.app` nem `*.vercel.app` via `bash_tool` (fora da lista de domínios permitidos), e as ferramentas disponíveis (`web_fetch_vercel_url`) só devolvem HTML estático — não executam JavaScript, por isso não conseguem exercitar os pedidos `fetch` que o frontend faz ao backend no browser.

O que *está* confirmado, de fontes primárias reais (não assumido):
- O backend está a responder (Railway confirma via o seu próprio healthcheck)
- O frontend serve o HTML/JS corretos, incluindo o URL do backend embutido no build
- CORS está configurado para aceitar pedidos do domínio do Vercel

O que falta confirmar és tu, ao abrir o link no telemóvel: cria uma memória de teste (ex. "o meu passaporte está no cofre"), confirma que aparece na lista, tenta pesquisar, edita, apaga. Se algo falhar, os logs do Railway (`get-logs` tipo `http`) vão mostrar exatamente o pedido e o erro.

---

## Estado da base de dados

PostgreSQL 16 no Railway, serviço `postgres`, status `SUCCESS`. Tabelas `memories` e `tasks` criadas via Alembic no arranque do backend, confirmadas nos logs de deploy.

## Problemas conhecidos

1. **Validação de CRUD em produção ainda não confirmada por mim** — pede-se o teu teste no telemóvel (ver acima).
2. **Sem autenticação** — a API e o frontend estão publicamente acessíveis sem login. Aceitável para esta fase de uso pessoal, mas a documentar antes de partilhares o link com mais alguém.
3. **URL do backend fixado no código-fonte** (não é uma variável de ambiente) devido às limitações do deploy direto por ficheiros do Vercel. Se no futuro ligares a GitHub App do Vercel (um clique em https://github.com/apps/vercel) e migrares para deploy via Git, isto pode voltar a ser uma variável de ambiente `NEXT_PUBLIC_API_BASE_URL` configurada no dashboard do Vercel.
4. **Sem domínio personalizado** — usa os URLs `*.vercel.app` / `*.up.railway.app` gerados automaticamente.
