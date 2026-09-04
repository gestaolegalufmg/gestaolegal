---
name: mobilizar-obras
description: Mobiliza de uma vez todos os canteiros liberados pela compatibilização — lê scripts/helton/projects/plans/manifest.json, monta a worktree e a stack de cada plano marcado como parallel, gera o cronograma (prd.json) de cada um e entrega o roteiro dos terminais a abrir. Use quando o usuário pedir "mobiliza as obras", "monta os canteiros", "sobe as worktrees dos planos", "prepara tudo para rodar em paralelo" ou quiser provisionar mais de um plano de uma vez.
---

# Mobilizar obras

Skill fina sobre script gordo: quem provisiona é o
`scripts/helton/obra/montar-canteiro.sh`. Aqui só se lê o manifesto, se chama o script
na ordem certa, se gera o cronograma de cada canteiro e se confere que cada um
nasceu inteiro.

## Pré-condições

Rode **do checkout principal**, na `develop`. Antes de tocar em qualquer
coisa, confira e pare no primeiro problema:

1. `scripts/helton/projects/plans/manifest.json` existe. Se não, ofereça rodar `/compatibilizar` — sem
   manifesto não há como saber o que pode ir em paralelo, e adivinhar aqui é o
   erro exato que a esteira existe para evitar.
2. **A árvore está limpa e o que importa está commitado.** Worktree só enxerga o
   commitado: script, `.env.worktree`, seed e skills que não estejam no commit
   simplesmente não existem lá dentro, e a falha aparece longe da causa. Rode
   `git status --porcelain` e, se houver pendência nesses caminhos, pare e diga
   o que falta commitar.
3. `git fetch origin` e `origin/develop` acessível.

## Procedimento

### 1. Ler o manifesto e separar

- `parallel` → mobiliza agora.
- `serialized_after:<plano>` → **não** mobiliza. Anote atrás de quem está.
- `needs_reslicing` → não mobiliza. Anote que o plano precisa ser reescrito.

Se a lista de `parallel` vier vazia, diga isso e pare.

### 2. Confirmar o tamanho da mobilização

Cada canteiro é uma stack Docker inteira (Postgres, API, nginx, Mailpit). Antes
de montar mais de três, avise o custo de máquina e confirme com o usuário
quantos ele quer de fato — é reversível, mas desmontar dá trabalho e o
"port is already allocated" de uma máquina sem fôlego aparece no meio.

### 3. Montar, um a um

Para cada plano `parallel`, em sequência (nunca em paralelo — os scripts
disputam a mesma sondagem de portas):

```bash
./scripts/helton/obra/montar-canteiro.sh <plano>
```

Se um falhar, **pare a mobilização** e relate. Não siga para o próximo: uma
falha aqui costuma ser de ambiente (porta, Docker, migration) e vai se repetir
em todos.

### 4. Gerar o cronograma de cada canteiro

Para cada canteiro montado, siga a skill `/cronograma` tomando
`../<projeto>-<plano>` como raiz — todos os caminhos daquela execução
(`scripts/helton/projects/plans/<plano>.md`, `scripts/helton/projects/prds/prd.json`) são relativos a **essa**
worktree, não ao checkout principal.

Faça um canteiro por vez, do começo ao fim, antes de começar o próximo. O
`/cronograma` tem fase de perguntas; misturar dois planos na mesma conversa é
como as respostas vão parar no prd errado.

Se preferir isolar de verdade, é legítimo pedir ao usuário que abra uma sessão
por worktree e rode `/cronograma` em cada uma — diga isso quando forem mais de
dois planos, porque o contexto de um plano polui o julgamento do outro.

### 5. Conferir que cada canteiro nasceu inteiro

Para cada um, todas as quatro:

```bash
test -f ../<projeto>-<plano>/scripts/helton/projects/prds/prd.json
jq -e '.userStories | length > 0' ../<projeto>-<plano>/scripts/helton/projects/prds/prd.json
grep -E '^(COMPOSE_PROJECT_NAME|APP_PORT|DB_PORT|NGINX_PORT)=' ../<projeto>-<plano>/.env
docker compose -p <projeto>-<plano> ps
```

Canteiro que falhe qualquer uma delas não está pronto; diga qual e o que falta.

### 6. Entregar o roteiro

Termine com a tabela do que ficou de pé — um bloco por canteiro, com worktree,
branch, portas e número de stories — e, para cada um, o comando do **ensaio**:

```bash
cd ../<projeto>-<plano> && ./scripts/helton/helton.sh --tool claude 1
```

Diga com todas as letras: **uma iteração vigiada por canteiro antes do AFK.** O
ensaio é o que prova que o commit cai na branch certa, que o compose isolado
responde e que o seed satisfaz os `verify`. Só depois dele se libera o cap real
(5–10 para fatia pequena, 30–50 para grande), um terminal por worktree.

Liste também, ao fim, os planos que **não** foram mobilizados e por quê — os
`serialized_after` voltam para cá quando o predecessor mergear.

## Fronteiras

- Não dispare o `helton.sh`. Nem o ensaio: quem decide começar é o usuário.
- Não faça merge nem abra PR. A colheita é do
  `scripts/helton/obra/desmontar-canteiro.sh` e do merge em fila, um de cada vez.
- Não mobilize plano `serialized_after` "porque o predecessor está quase" —
  quase não é mergeado.
