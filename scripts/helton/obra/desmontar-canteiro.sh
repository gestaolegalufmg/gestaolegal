#!/usr/bin/env bash
# desmontar-canteiro.sh <plano> [--volumes] [--force]
#
# Desmonta a worktree de um plano: compose down, worktree remove.
# A BRANCH helton/<plano> é preservada — ela é o entregável para o merge.
# Antes de desmontar, imprime o índice de revisão (o que o prd.json diz que foi
# feito, o que pede revisão e o que ficou barrado), que é o roteiro do PR.
#
#   --volumes  também remove os volumes do compose (perde o banco da worktree)
#   --force    remove a worktree mesmo com mudanças não commitadas

set -euo pipefail
die() { echo "desmontar-canteiro: erro: $*" >&2; exit 1; }

PLAN="${1:?uso: desmontar-canteiro.sh <plano> [--volumes] [--force]}"; shift || true
VOLUMES=""; FORCE=""
for a in "$@"; do case "$a" in
  --volumes) VOLUMES="--volumes" ;;
  --force)   FORCE="--force" ;;
  *) die "opção desconhecida: $a" ;;
esac; done

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "rode de dentro do repositório"
PROJECT="$(basename "$REPO_ROOT")"
NAME="$PROJECT-$PLAN"
WT_DIR="$(dirname "$REPO_ROOT")/$NAME"
[[ -d "$WT_DIR" ]] || die "worktree $WT_DIR não existe"

# ── Índice de revisão para o merge ───────────────────────────────────
PRD="$WT_DIR/scripts/helton/projects/prds/prd.json"
if [[ -f "$PRD" ]]; then
  python3 - "$PRD" <<'PY' || true
import json, sys

prd = json.load(open(sys.argv[1]))
# O schema deste repositório é {branchName, description, project, userStories}.
# Os outros nomes ficam aceitos porque o prd.json.example do upstream usa
# "tasks", e prd escrito à mão às vezes é só a lista.
if isinstance(prd, list):
    stories = prd
else:
    stories = prd.get("userStories") or prd.get("tasks") or []

def label(s):
    return s.get("title") or s.get("task") or ""

done  = [s for s in stories if s.get("passes")]
rev   = [s for s in stories if s.get("review_required")]
gated = [s for s in stories if s.get("human_gate") and not s.get("passes")]

print(f"── prd.json: {len(done)}/{len(stories)} concluídas ──")
if rev:
    print("REVISAR NO MERGE (review_required):")
    for s in rev:
        mark = "✔" if s.get("passes") else "✘ (não executada)"
        print(f"  {mark} [{s.get('id','?')}] {label(s)[:80]}")
if gated:
    print("FICARAM BARRADAS (human_gate, não executadas):")
    for s in gated:
        motivo = s.get("gate_reason") or "sem motivo registrado"
        print(f"  ⏸ [{s.get('id','?')}] {label(s)[:80]}")
        print(f"      motivo: {motivo[:100]}")
pend = [s for s in stories if not s.get("passes") and not s.get("human_gate")]
if pend:
    print(f"NÃO CONCLUÍDAS por outro motivo: {len(pend)}")
    for s in pend:
        print(f"  · [{s.get('id','?')}] {label(s)[:80]}")
PY
else
  echo "(sem $PRD na worktree — nada a reportar)"
fi
echo ""

# ── Guarda: trabalho não commitado ───────────────────────────────────
if [[ -z "$FORCE" ]] && [[ -n "$(git -C "$WT_DIR" status --porcelain)" ]]; then
  die "há mudanças não commitadas em $WT_DIR (commite, ou use --force para descartar)"
fi

# ── Desmonta ─────────────────────────────────────────────────────────
if [[ -f "$WT_DIR/.env" ]]; then
  ( cd "$WT_DIR" && docker compose -p "$NAME" down $VOLUMES ) || true
  echo "✔ compose '$NAME' derrubado ${VOLUMES:+(com volumes)}"
fi
git -C "$REPO_ROOT" worktree remove $FORCE "$WT_DIR"
echo "✔ worktree removida — branch helton/$PLAN preservada para o merge"
