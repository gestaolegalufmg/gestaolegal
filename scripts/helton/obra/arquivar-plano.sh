#!/usr/bin/env bash
# arquivar-plano.sh <plano> [--force]
#
# Tira um plano entregue de `scripts/helton/projects/plans/` e o guarda em `scripts/helton/projects/plans/implemented/`, para que a
# esteira pare de tratá-lo como trabalho pendente.
#
# **Por que este passo existe.** Depois do merge, a branch `helton/<plano>` é
# apagada e a worktree já foi no desmonte — de modo que NENHUMA das três guardas
# do `montar-canteiro.sh --todos` dispara (canteiro montado? não; branch existe?
# não; status no manifesto? ainda `parallel`). Sem arquivar, um plano já entregue
# ganha canteiro novo e o loop o refaz do zero.
#
# Roda DEPOIS do merge, do checkout principal:
#
#   ./scripts/helton/obra/desmontar-canteiro.sh onda-2     # colheita, branch preservada
#   git merge --no-ff helton/onda-2                  # à mão, quando o Roberto pedir
#   ./scripts/helton/obra/arquivar-plano.sh onda-2         # e só então o plano sai de scripts/helton/projects/plans/
#
#   --force   arquiva mesmo com a branch por mergear (para plano abandonado)

set -euo pipefail
die() { echo "arquivar-plano: erro: $*" >&2; exit 1; }
say() { echo "arquivar-plano: $*"; }

CONF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/obra.conf"
[[ -f "$CONF" ]] || die "falta $CONF"
# shellcheck source=obra.conf
source "$CONF"
[[ -n "${BASE_BRANCH:-}" ]] || die "BASE_BRANCH não definido em $CONF"

# ── Argumentos ───────────────────────────────────────────────────────
PLAN=""; FORCE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1 ;;
    -*)      die "opção desconhecida: $1 (só existe --force)" ;;
    *)       [[ -z "$PLAN" ]] || die "um plano por vez: já recebi '$PLAN'."
             PLAN="$1" ;;
  esac
  shift
done
[[ -n "$PLAN" ]] || die "uso: arquivar-plano.sh <plano> [--force]"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "rode de dentro do repositório"
PROJECT="$(basename "$REPO_ROOT")"
PARENT="$(dirname "$REPO_ROOT")"
BRANCH="helton/$PLAN"
ORIGEM="scripts/helton/projects/plans/$PLAN.md"
DESTINO="scripts/helton/projects/plans/implemented/$PLAN.md"

# ── O plano existe, é rastreado, e o destino está livre? ─────────────
if [[ ! -f "$REPO_ROOT/$ORIGEM" ]]; then
  [[ -f "$REPO_ROOT/$DESTINO" ]] && die "$ORIGEM já está em scripts/helton/projects/plans/implemented/ — nada a fazer."
  die "não achei $ORIGEM (nem em scripts/helton/projects/plans/implemented/).
   Confira o nome: é o mesmo do canteiro e da branch."
fi
[[ ! -e "$REPO_ROOT/$DESTINO" ]] \
  || die "já existe $DESTINO. Duas empreitadas com o mesmo nome é ambiguidade que
   não cabe aqui — renomeie uma das duas antes de arquivar."
git -C "$REPO_ROOT" ls-files --error-unmatch "$ORIGEM" >/dev/null 2>&1 \
  || die "$ORIGEM não está versionado. Um plano que nunca foi commitado também
   nunca chegou à base, logo nunca virou canteiro — se é rascunho a descartar,
   mova à mão."

# ── O canteiro já foi desmontado? ────────────────────────────────────
# Arquivar com a worktree de pé é declarar encerrado o que ainda está na bancada.
if [[ -e "$PARENT/$PROJECT-$PLAN" ]]; then
  die "o canteiro ainda está montado em $PARENT/$PROJECT-$PLAN.
   Desmonte antes: ./scripts/helton/obra/desmontar-canteiro.sh $PLAN"
fi

# ── Índice limpo? ────────────────────────────────────────────────────
# Este script commita. Se houver coisa no stage, ela entraria de carona num
# commit que deveria falar só do arquivamento.
git -C "$REPO_ROOT" diff --cached --quiet \
  || die "há mudanças no stage. Commite ou desfaça antes — este commit é só
   sobre o arquivamento, e não deve levar carona."

# ── A empreitada foi entregue? ───────────────────────────────────────
# O sinal é a branch estar contida na base. Se ela já nem existe, é o estado
# normal de quem mergeou e apagou (`git branch -d` só apaga o que foi mergeado).
say "buscando $BASE_BRANCH..."
git -C "$REPO_ROOT" fetch origin --quiet
git -C "$REPO_ROOT" rev-parse --verify --quiet "$BASE_BRANCH" >/dev/null \
  || die "$BASE_BRANCH não existe depois do fetch"

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  if git -C "$REPO_ROOT" merge-base --is-ancestor "$BRANCH" "$BASE_BRANCH"; then
    ENTREGA="branch $BRANCH mergeada em $BASE_BRANCH"
  elif [[ -n "$FORCE" ]]; then
    ENTREGA="branch $BRANCH NÃO mergeada — arquivado com --force"
    say "ATENÇÃO: $ENTREGA"
  else
    die "a branch $BRANCH existe e ainda NÃO está em $BASE_BRANCH.
   Arquivar agora marcaria como entregue um trabalho que ainda pode mudar — ou
   ser abandonado. Faça o merge primeiro; se o plano foi descartado de
   propósito, use --force."
  fi
else
  ENTREGA="branch $BRANCH não existe mais (mergeada e apagada)"
fi

# ── Move e commita ───────────────────────────────────────────────────
mkdir -p "$REPO_ROOT/scripts/helton/projects/plans/implemented"
git -C "$REPO_ROOT" mv "$ORIGEM" "$DESTINO"
git -C "$REPO_ROOT" commit --quiet \
  -m "chore(obra): arquiva o plano '$PLAN' em scripts/helton/projects/plans/implemented/" \
  -m "Empreitada encerrada — $ENTREGA.

Plano entregue que fica em scripts/helton/projects/plans/ volta a ser montado: depois do merge a branch
some e a worktree já foi, então nenhuma guarda do montar-canteiro.sh --todos
dispara e o loop refaria o trabalho do zero."

say "✔ $ORIGEM → $DESTINO"
say "  $ENTREGA"

# ── Manifesto e resto ────────────────────────────────────────────────
# O manifesto não impede nada (a enumeração do --todos sai de `scripts/helton/projects/plans/*.md`, não
# dele), mas listar um plano que já saiu confunde quem for ler.
if [[ -f "$REPO_ROOT/scripts/helton/projects/plans/manifest.json" ]] \
   && grep -q "\"$PLAN\"" "$REPO_ROOT/scripts/helton/projects/plans/manifest.json"; then
  say "  nota: scripts/helton/projects/plans/manifest.json ainda lista '$PLAN'. Rode /compatibilizar
   antes da próxima rodada, para regravá-lo sem ele."
fi

restantes="$( (cd "$REPO_ROOT/scripts/helton/projects/plans" && ls -1 *.md 2>/dev/null | grep -vx 'README.md') || true )"
echo ""
if [[ -n "$restantes" ]]; then
  echo "Planos ainda em scripts/helton/projects/plans/:"
  printf '  · %s\n' $restantes
else
  echo "Nenhum plano pendente em scripts/helton/projects/plans/."
fi
echo ""
echo "A base só enxerga o arquivamento depois do push:  git push ${BASE_BRANCH%%/*} ${BASE_BRANCH#*/}"
