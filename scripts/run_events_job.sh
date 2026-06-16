#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/events-$(date +%Y%m%d).log"
VENV_ACTIVATE="${PROJECT_DIR}/.venv/bin/activate"

mkdir -p "${LOG_DIR}"
cd "${PROJECT_DIR}"

export TZ=America/Sao_Paulo

if [[ ! -f "${VENV_ACTIVATE}" ]]; then
  echo "Erro: venv não encontrado em ${VENV_ACTIVATE}" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "${VENV_ACTIVATE}"

{
  echo "=== Eventos — Radar Financeiro - $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
  python run_events_job.py
  echo "=== Concluído - $(date '+%Y-%m-%d %H:%M:%S %Z') ==="
} >> "${LOG_FILE}" 2>&1
