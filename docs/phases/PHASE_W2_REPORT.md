# PHASE W2 — Repository Scaffolding + Frontend Foundation

**Status:** Implementado e verificado. Aguarda aprovação antes de avançar para a PHASE W3.
**Escopo:** Steps 1–2 do plano geral (repositório + fundação do frontend Next.js). Nenhum backend, base de dados, ou lógica de negócio foi tocado — conforme acordado.

---

## 1. Ficheiros criados

### Estrutura de repositório
```
nexus-web/
├── README.md
├── .gitignore
├── frontend/                          (Next.js — ver abaixo)
├── backend/                           (vazio — Phase W3)
├── docs/
│   ├── architecture/PHASE_W1_ARCHITECTURE.md   (movido para cá)
│   └── phases/PHASE_W2_REPORT.md               (este ficheiro)
└── infrastructure/
    ├── docker/ (vazio — Phase W4+)
    ├── postgres/ (vazio — Phase W4)
    └── env/ (vazio)
```

### Frontend (`nexus-web/frontend/`)
- `app/layout.tsx` — root layout: fontes self-hosted, `ThemeProvider`, `suppressHydrationWarning`
- `app/page.tsx` — redireciona `/` → `/now`
- `app/globals.css` — tokens de design (paleta light/dark, tipografia, radius, foco visível, `prefers-reduced-motion`)
- `app/(auth)/.gitkeep` — grupo de rotas reservado para a fase de Security
- `app/(dashboard)/layout.tsx` — envolve todos os módulos na `AppShell`
- `app/(dashboard)/{now,memory,tasks,documents,inventory,timeline,search}/page.tsx` — sete rotas placeholder, cada uma explicitamente rotulada com a fase que a implementa
- `components/layout/app-shell.tsx` — composição do rail + topbar + conteúdo
- `components/layout/nav-rail.tsx` — navegação principal (desktop), o elemento de assinatura visual
- `components/layout/mobile-nav.tsx` — navegação equivalente para ecrãs pequenos
- `components/layout/theme-provider.tsx` — wrapper de `next-themes`
- `components/layout/theme-toggle.tsx` — alternância dark/light
- `components/ui/button.tsx` — primitivo shadcn-style (autoria manual — ver secção 4)
- `components/features/module-placeholder.tsx` — placeholder explícito e documentado, partilhado pelos sete módulos
- `lib/utils.ts` — `cn()`
- `lib/api/client.ts` — placeholder da única porta de saída para o backend; lança erro explícito em vez de simular uma resposta
- `config/navigation.ts` — fonte única de verdade da lista de módulos
- `components.json` — configuração shadcn (para compatibilidade futura com a CLI, caso o registo fique acessível)
- `README.md` — substituído o boilerplate do `create-next-app` por documentação real do projeto

### Ficheiros modificados
- `package.json` — dependências adicionadas (ver secção 3)
- Removidos: `AGENTS.md`, `CLAUDE.md` (gerados automaticamente pelo `create-next-app`, não fazem parte do nosso processo documentado), `public/*.svg` (assets de template não utilizados)

---

## 2. Explicação de design (recapitulação)

Direção visual: um arquivo/catálogo pessoal, não um dashboard SaaS genérico. Paleta papel+tinta com um accent verde-azeitona (evita deliberadamente o creme+terracota e o preto+neon que dominam o design gerado por IA por defeito). Tipografia: Fraunces (display serif, itálico nos títulos de módulo) + Inter (corpo) + IBM Plex Mono (metadados). Assinatura: o separador ativo na coluna de navegação recebe um traço vertical sólido e o rótulo passa a versalete com tracking largo — como uma aba de pasta suspensa em destaque. Verificado visualmente por screenshot em light e dark mode (ver secção 5).

---

## 3. Dependências adicionadas

```
next 16.3.1, react 19.2.8, react-dom 19.2.8
tailwindcss ^4, @tailwindcss/postcss ^4
typescript ^5, eslint ^9, eslint-config-next 16.3.1
clsx, tailwind-merge, class-variance-authority, @radix-ui/react-slot
lucide-react, next-themes
@fontsource/fraunces, @fontsource/inter, @fontsource/ibm-plex-mono
```

Todas instaladas via `pnpm` a partir do registo npm (domínio permitido nesta sandbox).

---

## 4. Desvios do plano original (e porquê)

| Desvio | Motivo | Impacto |
|---|---|---|
| `shadcn/ui` CLI (`pnpm dlx shadcn init`) falhou: `ui.shadcn.com` não está na lista de domínios permitidos nesta sandbox (erro 403/"not authorized") | Ambiente sem acesso a esse domínio | Construí manualmente o equivalente shadcn (`cn()`, `Button` com `cva`, `components.json`) usando apenas pacotes do registo npm. Resultado funcionalmente equivalente; se o ambiente de deployment tiver acesso ao registo shadcn, a CLI pode ser usada normalmente a partir daqui, respeitando o `components.json` já criado. |
| `next/font/google` (Fraunces/Inter/IBM Plex Mono) falhou no build: `fonts.googleapis.com` não está na lista de domínios permitidos | Mesma causa | Troquei para `@fontsource/*` (fontes self-hosted, instaladas via npm, sem pedido de rede em runtime). Esta é geralmente a escolha de produção preferível de qualquer forma — sem dependência de terceiros em runtime, melhor privacidade e melhor performance. |

Nenhum destes desvios altera a arquitetura aprovada na W1; ambos são substituições de implementação dentro do mesmo contrato (tema, tipografia, componentes shadcn-style).

---

## 5. Revisão estática

- **Fronteiras de dependência:** confirmado por `grep` que nenhum componente chama `fetch()` diretamente — `lib/api/client.ts` é o único ponto de saída, conforme a regra da W1 (secção 3).
- **Sem conteúdo fake:** confirmado por `grep` que as únicas ocorrências de "placeholder"/"fake" no código são comentários que documentam explicitamente por que aquele código é um placeholder seguro (lança erro / mostra rótulo "NOT YET IMPLEMENTED"), nunca lógica que simula um resultado real.
- **Sem `console.*` ou `TODO/FIXME` esquecidos.**
- **Acessibilidade base:** foco visível global via `:focus-visible` em `globals.css`; `prefers-reduced-motion` respeitado; `aria-current="page"` no item de navegação ativo; `aria-label` no botão de tema.
- **Responsividade:** `NavRail` oculto abaixo de `md`, substituído por `MobileNav` (faixa horizontal). Não testado em dispositivo físico, apenas por breakpoint Tailwind — reportado como limitação conhecida.

---

## 6. Verificação executada (real, não assumida)

| Verificação | Comando | Resultado |
|---|---|---|
| Lint | `pnpm lint` | ✅ 0 erros, 0 avisos |
| Build de produção | `pnpm build` | ✅ compilação e type-check bem-sucedidos; 8 rotas pré-renderizadas como conteúdo estático |
| Servidor real | `pnpm start -p 3311` + `curl` | ✅ `/` → `307` (redirect correto para `/now`); `/memory` → `200` |
| Renderização visual | Playwright, screenshot real das rotas `/memory` em light e dark mode | ✅ confirmado visualmente: paleta, tipografia, marca de módulo ativo, ícone do botão de tema, tudo conforme o desenho |

Nenhum destes resultados foi assumido ou extrapolado — todos foram efetivamente executados nesta sessão.

---

## 7. Checklist de verificação

- [x] Estrutura de repositório completa (`frontend/`, `backend/`, `docs/`, `infrastructure/`)
- [x] `docs/architecture/PHASE_W1_ARCHITECTURE.md` presente e é a fonte de verdade
- [x] Next.js App Router configurado
- [x] TypeScript configurado, `pnpm build` type-checks sem erros
- [x] Tailwind v4 configurado com tokens de design próprios (não defaults)
- [x] shadcn/ui equivalente funcional (`cn`, `Button`, `components.json`)
- [x] Sistema de layout (`AppShell`) implementado
- [x] Sistema de tema dark/light funcional e verificado visualmente
- [x] Navigation shell com os sete módulos, ligada a `config/navigation.ts`
- [x] Sete rotas de módulo existem, cada uma como placeholder explícito rotulado com a fase futura
- [x] Nenhuma lógica de negócio, chamada de API real, ou persistência implementada (fora de escopo, confirmado por revisão)
- [x] Nenhum `fetch()` fora de `lib/api/`
- [x] Lint limpo
- [x] Build de produção bem-sucedido
- [x] Servidor de produção testado com `curl` real
- [x] Renderização verificada por screenshot real (light + dark)

---

## 8. Testes executados

Nenhum teste automatizado (unitário/e2e) foi escrito nesta fase — não fazia parte do escopo de W2 (scaffolding de fundação). A verificação foi feita por lint, build, execução real do servidor, e inspeção visual, conforme secção 6.

## 9. Build status

✅ **Build bem-sucedido**, executado nesta sessão (`pnpm build`, ver output na secção 6). Não é uma afirmação sem verificação.

## 10. Problemas conhecidos

1. `ui.shadcn.com` e `fonts.googleapis.com` não são acessíveis a partir desta sandbox de desenvolvimento — mitigado (ver secção 4), mas a acessibilidade desses domínios num ambiente de deployment real deve ser confirmada se decidires no futuro usar a CLI do shadcn diretamente.
2. `MobileNav` foi verificado apenas por breakpoint no build de produção, não em dispositivo físico ou emulador móvel real.
3. `app/(auth)/` está vazio (apenas `.gitkeep`) — intencional, por estar fora do escopo desta fase; será preenchido quando a fase de Security for implementada.
4. Nenhum `.git` foi inicializado ainda neste ambiente — o repositório existe como estrutura de ficheiros, mas ainda não como repositório Git com histórico de commits. A decidir se deve ser inicializado nesta sandbox ou apenas no teu ambiente local/CI.

---

## 11. Próxima fase proposta

**PHASE W3 — FastAPI Backend Foundation** (Step 3): estrutura de API, injeção de dependência, sistema de configuração, logging, error handling, health endpoints. Nenhuma persistência ainda (isso é W4).

Aguardo aprovação antes de iniciar a W3.
