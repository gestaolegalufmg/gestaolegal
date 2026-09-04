# Helton Agent Instructions

You are an autonomous coding agent working on a software project.

## Your Task

1. Read the PRD at `prd.json` (in the same directory as this file)
2. Read the progress log at `progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, check it out; if it
   doesn't exist, create it following the project's git rules (see **Project rules** below).
4. Pick the story to work on — **the filter below, não só a prioridade**
5. Implement that single user story
6. Run the quality checks the root `CLAUDE.md` lists under **Comandos**
7. Update CLAUDE.md files if you discover reusable patterns (see below)
8. If checks pass, update the PRD to set `passes: true` for the completed story
9. Append your progress to `progress.txt`
10. Commit **everything together** — code, `prd.json` and `progress.txt` in the same
    commit — with message: `feat: [Story ID] - [Story Title]`

> **A contabilidade vem antes do commit, e vai dentro dele.** Enquanto os passos 8 e 9
> ficavam depois do commit, toda iteração terminava com `prd.json` e `progress.txt` sujos:
> a iteração seguinte varria a sujeira da anterior, e a **última** de cada rodada deixava
> a story implementada e commitada mas marcada `passes: false` — alguém tinha que fechar à
> mão. Se os checks falharem, não commite nada e não marque `passes: true`.

## Qual story pegar (passo 4)

Escolha a story não concluída (`passes: false`) de **maior prioridade** (menor
`priority`) que satisfaça as duas condições:

- `human_gate: false` — a story não foi barrada para decisão humana; e
- `blocked_by_gate: false` — nenhuma story barrada está na cadeia de
  `depends_on` dela.

`review_required: true` **não impede execução**. Ela marca trabalho que o humano
vai reler no merge, não trabalho proibido — execute normalmente.

Confira também que todas as `depends_on` da story escolhida já estão
`passes: true`. Se não estiverem, ela ainda não é a sua.

**Não altere `human_gate`, `gate_reason` nem `blocked_by_gate` de story
nenhuma.** Esses campos são a trava; mexer neles para se desbloquear é o caso
que a trava existe para impedir. Se você acha que uma story foi barrada por
engano, registre isso em `progress.txt` e escolha outra.

Se todas as stories restantes estiverem barradas ou bloqueadas, **pare** — emita
o sinal de conclusão (ver **Stop Condition**) e não invente trabalho fora do
prd.

## Project rules

The repository root `CLAUDE.md` is the single source of truth for branch naming, base branch,
quality commands, architecture and conventions. Read it and follow it. Do not restate its
rules here — a copy would drift.

Two adjustments, because you run inside an autonomous loop:

- **You are already in your worktree.** The root `CLAUDE.md` tells each agent to create one;
  that step was done by whoever launched `helton.sh`. Do not create another. Work where you are.
  If `branchName` doesn't exist yet, branch from the same base the root file prescribes for
  worktrees — a base configurada em `BASE_BRANCH` (`scripts/helton/obra/obra.conf`), never the
  repository default branch.
- **Commit narrowly.** `git add -A` is fine only because this worktree is yours alone. Stage
  the files you actually touched; never sweep the whole tree on a shared checkout.

## Progress Report Format

APPEND to progress.txt (never replace, always append):
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "this codebase uses X for Y")
  - Gotchas encountered (e.g., "don't forget to update Z when changing W")
  - Useful context (e.g., "the evaluation panel is in component X")
---
```

The learnings section is critical - it helps future iterations avoid repeating mistakes and understand the codebase better.

## Consolidate Patterns

If you discover a **reusable pattern** that future iterations should know, add it to the `## Codebase Patterns` section at the TOP of progress.txt (create it if it doesn't exist). This section should consolidate the most important learnings:

```
## Codebase Patterns
- Example: Use `sql<number>` template for aggregations
- Example: Always use `IF NOT EXISTS` for migrations
- Example: Export types from actions.ts for UI components
```

Only add patterns that are **general and reusable**, not story-specific details.

## Update CLAUDE.md Files

Before committing, check if any edited files have learnings worth preserving in nearby CLAUDE.md files:

1. **Identify directories with edited files** - Look at which directories you modified
2. **Check for existing CLAUDE.md** - Look for CLAUDE.md in those directories or parent directories
3. **Add valuable learnings** - If you discovered something future developers/agents should know:
   - API patterns or conventions specific to that module
   - Gotchas or non-obvious requirements
   - Dependencies between files
   - Testing approaches for that area
   - Configuration or environment requirements

**Examples of good CLAUDE.md additions:**
- "When modifying X, also update Y to keep them in sync"
- "This module uses pattern Z for all API calls"
- "Tests require the dev server running on PORT 3000"
- "Field names must match the template exactly"

**Do NOT add:**
- Story-specific implementation details
- Temporary debugging notes
- Information already in progress.txt

Only update CLAUDE.md if you have **genuinely reusable knowledge** that would help future work in that directory.

## Quality Requirements

- ALL commits must pass the quality checks named in the root `CLAUDE.md`
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

## Browser Testing (If Available)

For any story that changes UI, verify it in the browser. Which tool is real here, and the
manual consent step it needs, are in the root `CLAUDE.md` under **Automação de browser** and
in `docs/manual_dev.md`. Read those before trying anything else — the other tool names that
turn up are dead ends.

1. Navigate to the relevant page
2. Verify the UI changes work as expected
3. Take a screenshot if helpful for the progress log

If no browser tools are available, note in your progress report that manual browser verification is needed.

## Stop Condition

Depois de concluir uma story, veja se sobrou alguma **executável** — isto é,
`passes: false` **e** `human_gate: false` **e** `blocked_by_gate: false`.

Se não sobrou (todas passaram, ou as que faltam estão barradas ou bloqueadas),
feche a empreitada:

1. Imprima o **índice de revisão** — é o roteiro do PR, e é a única vez em que
   ele é montado por quem fez o trabalho:
   - as stories executadas com `review_required: true`, cada uma com o id e o
     que foi feito;
   - as stories que ficaram com `human_gate: true` sem executar, com o
     `gate_reason` — é o que a branch **não** contém, e quem for mergear precisa
     saber disso antes de olhar o diff.
2. Responda com:
   <promise>COMPLETE</promise>

Se ainda houver story executável, encerre a resposta normalmente — a próxima
iteração pega a seguinte.

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read the Codebase Patterns section in progress.txt before starting

## Ambiente desta worktree

**As portas estão no `.env` desta worktree — leia-o, não presuma.** Cada worktree tem a
sua faixa, e este arquivo é versionado: qualquer número escrito aqui seria o de outra
worktree assim que a branch fosse criada. Foi o que aconteceu até 08/08/2026, quando este
bloco ainda anunciava o ambiente do `platform-billing` para todo mundo.

```bash
grep -E '^(COMPOSE_PROJECT_NAME|NGINX_PORT|APP_PORT|DB_PORT|MAILPIT_UI_PORT)=' .env
```

- Front (nginx, é onde a UI se verifica): `http://localhost:$NGINX_PORT`
- API: `http://localhost:$APP_PORT` — o front fala com ela por `/api`, via proxy do nginx
- Banco: host `$DB_PORT`. É volume nomeado do projeto, não some sozinho
- Mailpit (e-mail capturado): `http://localhost:$MAILPIT_UI_PORT`

Se o `.env` não existir, a worktree ainda não tem ambiente — e não é você que monta. Pare e
diga isso: quem provisiona é o `scripts/helton/obra/montar-canteiro.sh`, rodado do checkout
principal, e é ele que escolhe a faixa de portas desviando das que os outros agentes já
tomaram. Copiar o `.env` do vizinho à mão é como duas stacks acabam brigando por porta ou,
pior, compartilhando banco sem ninguém perceber.

Regras:
- `docker compose` puro, sem `-f`. O projeto é o `COMPOSE_PROJECT_NAME` do `.env` desta
  worktree — é ele que mantém containers, rede e volumes separados dos outros agentes
- `docker compose exec <serviço>`, NUNCA `docker exec <nome>`: os containers não têm nome fixo
- Serviços desta stack: veja `SERVICES`, `DB_SERVICE` e `MIGRATE_SERVICE` em
  `scripts/helton/obra/obra.conf`, ou `docker compose ps`
- Mudou algo no front: `docker compose up -d --build <serviço do front>` antes de verificar a tela.
  Sem rebuild, o navegador mostra o bundle antigo e a verificação passa errada
- Migration nova: `docker compose up -d migrate` aplica; `make migrate` também serve
- Verificação de UI: plugin browser-use apontando para o `NGINX_PORT` desta worktree
