#!/usr/bin/env bash
# montar-canteiro.sh <plano>
# montar-canteiro.sh --todos
#
# Provisiona o canteiro de um plano: worktree própria, faixa de portas própria,
# stack Compose de pé e banco semeado. NÃO gera o prd.json e NÃO dispara o loop
# — isso é do `/cronograma` e do `helton.sh`, nessa ordem, já de dentro da
# worktree.
#
# O nome do plano é a chave primária de tudo:
#
#   scripts/helton/projects/plans/onda-2.md  ->  worktree ../<projeto>-onda-2
#                    ->  branch helton/onda-2
#                    ->  projeto Compose <projeto>-onda-2
#
# Com `--todos`, monta um canteiro para cada plano liberado pela
# compatibilização, um de cada vez.
#
# Uso:
#   ./scripts/helton/obra/montar-canteiro.sh onda-2
#   ./scripts/helton/obra/montar-canteiro.sh --todos
#   ./scripts/helton/obra/montar-canteiro.sh onda-2 --sem-deps   # sem node_modules/venv
#   cd ../<projeto>-onda-2 && claude   # e lá dentro: /cronograma

set -euo pipefail
die() { echo "montar-canteiro: erro: $*" >&2; exit 1; }
say() { echo "montar-canteiro: $*"; }

# ── Config do projeto ────────────────────────────────────────────────
# Tudo que é específico do repositório mora em obra.conf, ao lado deste script.
# É o único arquivo a editar para aplicar a esteira a outro projeto.
CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/obra.conf"
[[ -f "$CONF" ]] || { echo "montar-canteiro: erro: falta $CONF" >&2; exit 1; }
# shellcheck source=obra.conf
source "$CONF"

for v in BASE_BRANCH DB_SERVICE PORT_APP PORT_DB PORT_WEB PORT_MAIL LIMITE_SEM_PERGUNTAR; do
  [[ -n "${!v:-}" ]] || { echo "montar-canteiro: erro: $v não definido em $CONF" >&2; exit 1; }
done
declare -f instalar_dependencias >/dev/null \
  || { echo "montar-canteiro: erro: falta a função instalar_dependencias em $CONF" >&2; exit 1; }

# Constante do kit, não do projeto: é a linha que fecha o cabeçalho do
# `.env.worktree`, e tem de existir igual nos dois lados.
HEADER_END="# fim-do-cabecalho"
# `MONTAR_CANTEIRO_BASE_SHA` é contrato INTERNO entre a rodada `--todos` e os
# processos filhos: o pai resolve a base uma vez e a fixa num commit, e cada
# filho deriva dali em vez de reperguntar ao remoto. Não é para ser exportado à
# mão — quem quiser montar de outra base deve mudar BASE_BRANCH, que é a decisão
# de arquitetura, não um atalho de linha de comando.

nome_kebab() { [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; }

# ── Argumentos ───────────────────────────────────────────────────────
MODO="um"
PLAN=""
SEM_DEPS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --todos)    MODO="todos" ;;
    --sem-deps) SEM_DEPS=1 ;;
    -*)         die "opção desconhecida: $1 (existem --todos e --sem-deps)" ;;
    *)          [[ -z "$PLAN" ]] || die "um plano por vez: já recebi '$PLAN'. Para vários, --todos."
                PLAN="$1" ;;
  esac
  shift
done
[[ "$MODO" == "todos" || -n "$PLAN" ]] || die "uso: montar-canteiro.sh <plano> [--sem-deps]
                                     montar-canteiro.sh --todos [--sem-deps]"
[[ "$MODO" != "todos" || -z "$PLAN" ]] || die "--todos escolhe os planos sozinho; tire o '$PLAN'."

# ── Contexto do repositório ──────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "rode de dentro do repositório"
PROJECT="$(basename "$REPO_ROOT")"
PARENT="$(dirname "$REPO_ROOT")"
OVERLAY="$REPO_ROOT/.env.worktree"
BASE_ENV="$REPO_ROOT/.env.example"

[[ -f "$OVERLAY" ]]  || die "falta $OVERLAY — sem ele não há como isolar as portas"
[[ -f "$BASE_ENV" ]] || die "falta $BASE_ENV — é a base do .env da worktree"
[[ -w "$PARENT" ]]   || die "sem permissão de escrita em $PARENT"

# ═════════════════════════════════════════════════════════════════════
# --todos: escolhe os planos e delega cada um a um processo filho
# ═════════════════════════════════════════════════════════════════════
#
# **Cada canteiro roda como `"$0" <plano>`, processo separado, e não como função
# ou subshell deste script.** Não é preferência de estilo: `set -e` é desligado
# dentro de qualquer comando cujo status esteja sendo testado (`if`, `&&`, `!`),
# e isso vale para funções e subshells. Numa versão anterior, um `git worktree
# add` que falhava não abortava nada — o script seguia, escrevia `.env` num
# diretório inexistente, o `cd` falhava, e o `docker compose` acabava rodando no
# **checkout principal**, mexendo na stack de dev de quem chamou. Pior: como o
# status do subshell é o do último comando, o `if` ainda considerava o canteiro
# montado. Processo filho tem o próprio `set -e`, aborta na primeira falha e
# devolve o código de saída certo.
if [[ "$MODO" == "todos" ]]; then
  say "buscando $BASE_BRANCH..."
  git -C "$REPO_ROOT" fetch origin --quiet
  git -C "$REPO_ROOT" rev-parse --verify --quiet "$BASE_BRANCH" >/dev/null \
    || die "$BASE_BRANCH não existe depois do fetch"

  # Fixa a base da rodada num commit: todos os canteiros nascem do MESMO ponto.
  # Sem isto, um push na base no meio de uma rodada longa faria os
  # últimos canteiros nascerem de uma base diferente dos primeiros — e as
  # decisões do manifesto foram tomadas contra uma base só. De quebra, dispensa
  # o fetch de cada filho.
  BASE_SHA="$(git -C "$REPO_ROOT" rev-parse "$BASE_BRANCH")"
  export MONTAR_CANTEIRO_BASE_SHA="$BASE_SHA"
  say "base da rodada fixada em ${BASE_SHA:0:8}."

  # Os planos vêm da BASE, não da pasta local: é de lá que as worktrees nascem,
  # e plano que só existe aqui não teria como ser montado mesmo. Os locais que
  # ficaram de fora entram na lista de pulados, para o esquecimento de push não
  # passar em silêncio.
  mapfile -t NA_BASE < <(
    git -C "$REPO_ROOT" ls-tree --name-only "$BASE_SHA" scripts/helton/projects/plans/ \
      | sed -n 's|^scripts/helton/projects/plans/\(.*\)\.md$|\1|p' | grep -vx 'README' || true
  )

  # O manifesto do /compatibilizar também vem da base — é de lá que o
  # /cronograma vai lê-lo, de dentro de cada worktree. Sem manifesto, montar
  # tudo é uma aposta: o script avisa e segue, porque quem tem um plano só não
  # deve ser obrigado a compatibilizar nada.
  declare -A STATUS=()
  MANIFESTO="não"
  if git -C "$REPO_ROOT" cat-file -e "$BASE_SHA:scripts/helton/projects/plans/manifest.json" 2>/dev/null; then
    MANIFESTO="sim"
    while IFS=$'\t' read -r n s; do
      [[ -n "$n" ]] && STATUS["$n"]="$s"
    done < <(git -C "$REPO_ROOT" show "$BASE_SHA:scripts/helton/projects/plans/manifest.json" | python3 -c '
import json, sys
try:
    m = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for p in m.get("plans", []):
    print("%s\t%s" % (p.get("name", ""), p.get("status", "")))
')
  fi

  ESCOLHIDOS=()
  PULADOS=()
  for p in "${NA_BASE[@]}"; do
    if ! nome_kebab "$p"; then
      PULADOS+=("$p — nome não é kebab-case")
    elif [[ -e "$PARENT/$PROJECT-$p" ]]; then
      PULADOS+=("$p — canteiro já montado")
    elif git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/helton/$p"; then
      PULADOS+=("$p — branch helton/$p já existe (empreitada anterior por mergear)")
    elif [[ "$MANIFESTO" == "não" ]]; then
      ESCOLHIDOS+=("$p")
    else
      case "${STATUS[$p]:-ausente}" in
        parallel)           ESCOLHIDOS+=("$p") ;;
        serialized_after:*) PULADOS+=("$p — ${STATUS[$p]}: espera o predecessor mergear") ;;
        needs_reslicing)    PULADOS+=("$p — needs_reslicing: precisa ser reescrito antes") ;;
        ausente)            PULADOS+=("$p — fora do manifesto: rode /compatibilizar de novo") ;;
        *)                  PULADOS+=("$p — status desconhecido no manifesto: ${STATUS[$p]}") ;;
      esac
    fi
  done

  # Plano que existe aqui e não na base entra na mesma lista: silêncio sobre ele
  # é como um push esquecido vira "mas eu escrevi esse plano".
  for f in "$REPO_ROOT"/scripts/helton/projects/plans/*.md; do
    [[ -e "$f" ]] || continue
    n="$(basename "$f" .md)"
    [[ "$n" == "README" ]] && continue
    git -C "$REPO_ROOT" cat-file -e "$BASE_SHA:scripts/helton/projects/plans/$n.md" 2>/dev/null \
      || PULADOS+=("$n — existe só neste checkout: commite e faça push")
  done

  echo ""
  if [[ "$MANIFESTO" == "sim" ]]; then
    say "manifesto encontrado na base — montando só os planos 'parallel'."
  else
    say "ATENÇÃO: não há scripts/helton/projects/plans/manifest.json em $BASE_BRANCH.
   Sem compatibilização ninguém conferiu se estes planos disputam os mesmos
   arquivos, e dois canteiros que colidem só se descobrem no merge. Com mais de
   um plano, rode /compatibilizar antes."
  fi

  if [[ ${#PULADOS[@]} -gt 0 ]]; then
    echo ""
    echo "  Pulados (${#PULADOS[@]}):"
    printf '    · %s\n' "${PULADOS[@]}"
  fi

  [[ ${#ESCOLHIDOS[@]} -gt 0 ]] || { echo ""; say "nada a montar."; exit 0; }

  echo ""
  echo "  A montar (${#ESCOLHIDOS[@]}):"
  printf '    · %s\n' "${ESCOLHIDOS[@]}"
  echo ""

  # Cada canteiro é uma stack Docker inteira. Acima do limite, confirma — mas só
  # quando há alguém para responder; chamado de dentro de uma skill, segue.
  if [[ ${#ESCOLHIDOS[@]} -gt $LIMITE_SEM_PERGUNTAR && -t 0 ]]; then
    read -r -p "montar-canteiro: são ${#ESCOLHIDOS[@]} stacks Docker. Seguir? [s/N] " resposta
    [[ "$resposta" =~ ^[sS]$ ]] || { say "cancelado."; exit 0; }
  fi

  # Um de cada vez, nunca em paralelo: a sondagem de portas lê o `.env` dos
  # vizinhos, e dois scripts simultâneos escolheriam a mesma faixa.
  MONTADOS=()
  FALHOU=""
  for p in "${ESCOLHIDOS[@]}"; do
    echo ""
    echo "═══ canteiro '$p'  (${#MONTADOS[@]} de ${#ESCOLHIDOS[@]} prontos) ═══"
    if "$0" "$p" ${SEM_DEPS:+--sem-deps}; then
      MONTADOS+=("$p")
    else
      FALHOU="$p"
      break
    fi
  done

  echo ""
  echo "───────────────────────────────────────────────────────────────"
  if [[ ${#MONTADOS[@]} -gt 0 ]]; then
    echo "Canteiros montados (${#MONTADOS[@]}):"
    for p in "${MONTADOS[@]}"; do
      echo "  ✔ $p  →  $PARENT/$PROJECT-$p  (branch helton/$p)"
    done
  fi

  if [[ -n "$FALHOU" ]]; then
    echo ""
    echo "PAROU no canteiro '$FALHOU'. Os seguintes não foram tentados — falha aqui"
    echo "costuma ser de ambiente (porta, Docker, migration) e se repetiria em todos."
    exit 1
  fi

  echo ""
  echo "Em cada worktree, na ordem: /cronograma → ensaio de 1 iteração → cap real."
  exit 0
fi

# ═════════════════════════════════════════════════════════════════════
# Um plano
# ═════════════════════════════════════════════════════════════════════
nome_kebab "$PLAN" || die \
  "'$PLAN' não é kebab-case. O nome vira diretório, branch e projeto Compose —
   use apenas minúsculas, dígitos e hífen simples (ex.: onda-2, estoque-acerto)."

NAME="$PROJECT-$PLAN"
WT_DIR="$PARENT/$NAME"
BRANCH="helton/$PLAN"
PLAN_FILE="$REPO_ROOT/scripts/helton/projects/plans/$PLAN.md"

[[ ! -e "$WT_DIR" ]] || die "já existe $WT_DIR (desmonte antes: desmontar-canteiro.sh $PLAN)"
git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH" \
  && die "a branch $BRANCH já existe — ela é o entregável de uma empreitada
   anterior. Faça o merge (ou apague-a) antes de montar o canteiro de novo."

# ── O que a base carrega ─────────────────────────────────────────────
# Toda guarda daqui para baixo pergunta pela BASE, não pelo working tree deste
# checkout. A worktree só enxerga o commitado e pushado: arquivo que exista só
# aqui simplesmente não está lá dentro, e a falha aparece longe da causa (o
# seed estoura com "No module named", o /cronograma não acha o plano).
#
# Numa rodada `--todos` a base já vem resolvida e FIXADA pelo pai, em
# MONTAR_CANTEIRO_BASE_SHA — todos os canteiros da rodada nascem do mesmo
# commit, mesmo que alguém pushe na base no meio. Nesse caso não há
# fetch a fazer: o pai acabou de fazê-lo, e refazer só abriria a janela que a
# fixação fecha.
BASE_REF="$BASE_BRANCH"
BASE_LABEL="$BASE_BRANCH"
if [[ -n "${MONTAR_CANTEIRO_BASE_SHA:-}" ]]; then
  [[ "$(git -C "$REPO_ROOT" cat-file -t "$MONTAR_CANTEIRO_BASE_SHA" 2>/dev/null)" == "commit" ]] \
    || die "MONTAR_CANTEIRO_BASE_SHA='$MONTAR_CANTEIRO_BASE_SHA' não é um commit
   deste repositório. Ela é contrato interno do --todos; se você a exportou à
   mão, tire-a do ambiente."
  BASE_REF="$MONTAR_CANTEIRO_BASE_SHA"
  BASE_LABEL="$BASE_BRANCH @ ${MONTAR_CANTEIRO_BASE_SHA:0:8} (fixada pela rodada)"
else
  say "buscando $BASE_BRANCH..."
  git -C "$REPO_ROOT" fetch origin --quiet
  git -C "$REPO_ROOT" rev-parse --verify --quiet "$BASE_BRANCH" >/dev/null \
    || die "$BASE_BRANCH não existe depois do fetch"
fi

if ! git -C "$REPO_ROOT" cat-file -e "$BASE_REF:scripts/helton/projects/plans/$PLAN.md" 2>/dev/null; then
  [[ -f "$PLAN_FILE" ]] && die \
    "scripts/helton/projects/plans/$PLAN.md existe neste checkout, mas não em $BASE_LABEL.
   Commite e faça push antes de montar o canteiro — a worktree é derivada da
   base, e lá dentro o /cronograma não acharia o plano."
  die "plano não existe: scripts/helton/projects/plans/$PLAN.md
   (o canteiro é montado para um plano aprovado; escreva-o, commite e faça push)"
fi

faltando=""
for p in "${ESTEIRA[@]}"; do
  git -C "$REPO_ROOT" cat-file -e "$BASE_REF:$p" 2>/dev/null || faltando="$faltando
     - $p"
done
[[ -z "$faltando" ]] || die "a esteira não está em $BASE_LABEL:$faltando
   Faça o merge (e push) da branch da esteira na base antes de montar
   canteiro. Sem isso a worktree nasce sem seed, sem loop e sem as skills, e só
   descobre no meio do provisionamento."

# ── Worktree ─────────────────────────────────────────────────────────
git -C "$REPO_ROOT" worktree add "$WT_DIR" -b "$BRANCH" "$BASE_REF"
# Criada a partir de um SHA, a branch não ganha upstream (criada a partir de
# de uma ref remota, ganha). Igualar os dois casos mantém o `git status` da
# worktree dizendo o quanto ela está à frente da base.
[[ "$BASE_REF" == "$BASE_BRANCH" ]] \
  || git -C "$WT_DIR" branch --set-upstream-to="$BASE_BRANCH" "$BRANCH" >/dev/null
say "✔ worktree $WT_DIR na branch $BRANCH (a partir de $BASE_LABEL)"

# ── Empreitada anterior ──────────────────────────────────────────────
# `scripts/helton/projects/prds/prd.json` e `progress.txt` são versionados, então a worktree
# nasce com a empreitada que estava na base. O `.last-branch` NÃO vem junto (é
# gitignored), de modo que o arquivamento automático do `helton.sh` nem dispara:
# um ensaio rodado antes do `/cronograma` leria o prd velho e, seguindo o
# `scripts/helton/CLAUDE.md`, faria checkout da branch DELE — o trabalho cairia
# fora de $BRANCH. Por isso o canteiro nasce limpo. Nada se perde: o conteúdo
# removido continua em $BASE_BRANCH:scripts/helton/.
WT_PRD="$WT_DIR/scripts/helton/projects/prds/prd.json"
WT_PROGRESS="$WT_DIR/scripts/helton/projects/prds/progress.txt"
anterior=""; limpou=""
if [[ -f "$WT_PRD" ]]; then
  anterior="$(sed -n 's/.*"branchName"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$WT_PRD" | head -1)"
  rm -f "$WT_PRD"
  limpou="prd.json"
fi
if [[ -f "$WT_PROGRESS" ]]; then
  # Preserva só a seção `## Codebase Patterns` do topo — é conhecimento que
  # atravessa empreitadas e que o loop lê antes de começar. O log por story da
  # empreitada anterior (tudo a partir do primeiro `## [`) sai.
  awk '/^## \[/ { exit } { print }' "$WT_PROGRESS" > "$WT_PROGRESS.novo"
  {
    echo "## Empreitada: $PLAN ($BRANCH) — canteiro montado em $(date +%Y-%m-%d)"
    echo "Log da anterior${anterior:+ ($anterior)}: $BASE_REF:scripts/helton/projects/prds/progress.txt"
    echo "---"
  } >> "$WT_PROGRESS.novo"
  mv "$WT_PROGRESS.novo" "$WT_PROGRESS"
  limpou="${limpou:+$limpou e }progress.txt"
fi
if [[ -n "$limpou" ]]; then
  git -C "$WT_DIR" add -A scripts/helton
  git -C "$WT_DIR" commit --quiet \
    -m "chore(obra): limpa a empreitada anterior no canteiro '$PLAN'" \
    -m "prd.json removido e progress.txt reduzido à seção Codebase Patterns, para
que um ensaio rodado antes do /cronograma não execute o prd da empreitada
anterior nem faça checkout da branch dela. O conteúdo segue em
$BASE_REF:scripts/helton/projects/prds/."
  say "✔ canteiro limpo da empreitada anterior${anterior:+ ($anterior)} — $limpou"
fi

# ── Faixa de portas ──────────────────────────────────────────────────
# Offset determinístico a partir do nome (mesmo plano, mesma faixa sempre), com
# sondagem linear contra o que as worktrees vizinhas já reservaram. Múltiplo de
# 10 na faixa 100–990: 90 vagas, e a aritmética das bases no .env.worktree
# garante que as famílias de porta não se cruzem.
SLOTS=90
sum="$(printf '%s' "$PLAN" | cksum | cut -d' ' -f1)"
slot=$(( sum % SLOTS ))

taken=""
for d in "$PARENT/$PROJECT"-*/; do
  [[ -f "$d/.env" ]] || continue
  o="$(grep -m1 -oE '^HELTON_OFFSET=[0-9]+' "$d/.env" | cut -d= -f2 || true)"
  [[ -n "$o" ]] && taken="$taken $o"
done

OFFSET=""
for _ in $(seq 1 "$SLOTS"); do
  candidate=$(( slot * 10 + 100 ))
  if [[ " $taken " != *" $candidate "* ]]; then OFFSET="$candidate"; break; fi
  slot=$(( (slot + 1) % SLOTS ))
done
[[ -n "$OFFSET" ]] || die "as 90 faixas de porta estão ocupadas — desmonte algum canteiro"
say "✔ faixa de portas: offset $OFFSET ($LABEL_APP $((PORT_APP+OFFSET)), $LABEL_DB $((PORT_DB+OFFSET)), $LABEL_WEB $((PORT_WEB+OFFSET)), $LABEL_MAIL $((PORT_MAIL+OFFSET)))"

# ── .env da worktree ─────────────────────────────────────────────────
# Base = .env.example menos as chaves que o overlay redefine; depois o overlay
# resolvido. Filtrar em vez de confiar em "a última atribuição vence" deixa o
# arquivo legível e não depende da ordem de leitura do dotenv.
#
# Do overlay entra só o que vem DEPOIS da linha marcadora: o cabeçalho documenta
# o próprio overlay e, pior, seus exemplos com `{{PORT:...}}` seriam substituídos
# junto — o .env de um canteiro de offset 200 acabava explicando que
# "5200 -> 5300".
OVERLAY_BODY="$(awk -v m="$HEADER_END" 'passou { print } $0 == m { passou = 1 }' "$OVERLAY")"
[[ -n "$OVERLAY_BODY" ]] || die "não achei conteúdo depois de '$HEADER_END' em $OVERLAY
   — é essa linha que separa a documentação do overlay do que vai para o .env"
keys="$(printf '%s\n' "$OVERLAY_BODY" | grep -oE '^[A-Z_][A-Z0-9_]*=' | tr -d '=' | paste -sd'|' -)"
{
  echo "# GERADO por scripts/helton/obra/montar-canteiro.sh para o plano '$PLAN'."
  echo "# Base: .env.example  |  Overlay: .env.worktree  |  Offset: $OFFSET"
  echo "# Editar à mão é permitido; regenerar sobrescreve."
  echo ""
  # `|| true` porque grep sai 1 quando não imprime nada, e com `set -e` isso
  # abortava o script inteiro DENTRO do redirecionamento — sem mensagem, logo
  # depois de anunciar a faixa de portas. Acontece quando toda chave do
  # `.env.example` é redefinida pelo overlay (projeto pequeno, ou `.env.example`
  # ainda enxuto), e o sintoma é um `montar-canteiro.sh` que morre calado.
  grep -vE "^($keys)=" "$BASE_ENV" || true
  echo ""
  echo "# ── overlay da worktree ──────────────────────────────────────────"
  while IFS= read -r line; do
    line="${line//\{\{PROJECT\}\}/$NAME}"
    line="${line//\{\{OFFSET\}\}/$OFFSET}"
    while [[ "$line" =~ \{\{PORT:([0-9]+)\}\} ]]; do
      b="${BASH_REMATCH[1]}"
      line="${line//\{\{PORT:$b\}\}/$(( b + OFFSET ))}"
    done
    printf '%s\n' "$line"
  done <<< "$OVERLAY_BODY"
} > "$WT_DIR/.env"
say "✔ .env gerado ($NAME)"

# ── Stack ────────────────────────────────────────────────────────────
cd "$WT_DIR"
say "subindo o banco..."
docker compose up -d --wait "$DB_SERVICE"
say "aplicando migrations..."
# `run --rm` em vez de `up --exit-code-from migrate migrate`: o migrate é um
# serviço de uma tacada só (roda `alembic upgrade head` e sai).
#
# Medido neste repositório em 09/08/2026, com Compose v5.3.1: as duas formas
# empatam no que importa. As duas devolvem o código de saída do alembic (0 no
# caminho feliz, 1 com o banco inalcançável), nenhuma derruba o banco que
# já estava de pé — o `--abort-on-container-exit` implícito parou só o próprio
# migrate — e nenhuma entra em loop por causa do `restart: on-failure`. O que
# `run --rm` dá a mais é não deixar container parado no projeto e dispensar o
# `--exit-code-from`. É arrumação, não conserto: quem for mexer aqui não deve
# supor que a forma antiga tinha um bug.
if [[ -n "${MIGRATE_SERVICE:-}" ]]; then
docker compose run --rm "$MIGRATE_SERVICE" \
  || die "as migrations falharam — o canteiro ficou de pé para você investigar
   (docker compose logs $MIGRATE_SERVICE), e desmontar-canteiro.sh $PLAN --force limpa"
fi
# ── Dependências do host e tipos gerados ─────────────────────────────
# Duas coisas que o git não traz e sem as quais o PRIMEIRO `make ready` da
# worktree quebra: `web/node_modules` (quebra em web-help com
# ERR_MODULE_NOT_FOUND, no pacote `marked`) e `web/src/lib/gen/schema.ts`, que é
# gerado e está no .gitignore (quebra com "Property X does not exist", apontando
# para um front que está certo). Num loop autônomo isso queima a primeira
# iteração inteira, e a mensagem manda o agente investigar o lugar errado — por
# isso o canteiro já nasce com as duas.
#
# Roda ANTES de subir os SERVICES, e não depois. Serviço de dev que faz bind
# mount do código do host e o executa de lá (um `npm run dev` sobre
# `frontend/`, típico do Vite) não sobe sem as dependências instaladas: morre
# com `vite: not found` (exit 127) e leva o proxy junto (`host not found in
# upstream frontend:5173`). Visto no canteiro processo-seletivo do projeto de
# origem em 25/08/2026 — o `up --wait` "passou" com dois serviços mortos, e a
# causa só apareceu no `docker compose logs`.
#
# Custa disco: ~420 MB de node_modules e ~320 MB de .venv por canteiro (o venv
# sai quase todo em hardlink do cache do uv; o node_modules, não). Quem só quer
# olhar a tela usa `--sem-deps` e economiza os dois.
if [[ -n "$SEM_DEPS" ]]; then
  say "pulando as dependências do host (--sem-deps). Os serviços que dependem
   delas vão cair até você rodar, de dentro da worktree, o que está em
   instalar_dependencias() no obra.conf, seguido de 'docker compose up -d'.
   Use instalador que NÃO reescreve o lockfile ('npm ci', 'uv sync --locked')."
else
  # `npm ci`, e não `npm install`: o install reescreve o `package-lock.json`
  # (marca `"dev": true` em pacotes opcionais do rollup, entre outros) e o
  # canteiro nasceria com a árvore suja — o primeiro commit do loop, que usa
  # `git add -A`, varreria esse ruído para dentro da empreitada. O `ci` instala
  # exatamente o que o lockfile manda e nunca o altera.
  say "instalando as dependências do host (ver instalar_dependencias em obra.conf)..."
  instalar_dependencias \
    || die "instalar_dependencias falhou em $WT_DIR — banco e migrations estão de pé.
   Rode os comandos à mão lá dentro e depois 'docker compose up -d'; ou remonte
   com --sem-deps."
fi

say "subindo ${SERVICES[*]}..."
docker compose up -d --wait "${SERVICES[@]}"

# ── Seed ─────────────────────────────────────────────────────────────
if [[ ${#SEED_CMD[@]} -gt 0 ]]; then
say "semeando o banco..."
"${SEED_CMD[@]}" || die "o seed falhou — a stack está de pé, corrija e rode
   '${SEED_CMD[*]}' de dentro de $WT_DIR"
fi

# ── Pronto ───────────────────────────────────────────────────────────
cat <<EOF

✔ canteiro montado para '$PLAN'

  worktree : $WT_DIR
  branch   : $BRANCH
  compose  : $NAME
  $LABEL_WEB : http://localhost:$((PORT_WEB+OFFSET))
  $LABEL_APP : http://localhost:$((PORT_APP+OFFSET))
  $LABEL_DB : localhost:$((PORT_DB+OFFSET))
  $LABEL_MAIL : http://localhost:$((PORT_MAIL+OFFSET))

Próximo passo — de dentro da worktree:

  cd $WT_DIR
  claude          # e lá: /cronograma   (gera scripts/helton/projects/prds/prd.json)
  ./scripts/helton/helton.sh --tool claude 1    # ensaio de UMA iteração, vigiado

Só depois do ensaio limpo é que se libera o cap real da empreitada.
EOF
