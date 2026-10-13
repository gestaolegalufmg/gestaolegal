#!/usr/bin/env bash
# Reset não interativo para cron. Execute a partir do host Docker.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

# O arquivo permanece no disco; flock libera o lock ao encerrar o processo.
exec 9>.reset-demo.lock
flock -n 9 || { echo 'reset-demo: outra execução está em andamento.'; exit 1; }
service="${RESET_API_SERVICE:-api}"
compose=(docker compose)
run=("${compose[@]}" run --rm --no-deps -T --entrypoint python "$service" scripts/reset_demo_database.py)

# Valida o alvo antes de interromper a API.
"${run[@]}" --check
"${compose[@]}" stop "$service"
# Se falhar, deixa a API parada para não servir um banco parcial.
"${run[@]}"
"${compose[@]}" start "$service"
echo 'reset-demo: API iniciada.'
