#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"

read_env_var() {
  local key="$1"
  local default="$2"
  if [[ -f "${ENV_FILE}" ]]; then
    local value
    value="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n1 | cut -d= -f2- | tr -d '\r')"
    if [[ -n "${value}" ]]; then
      echo "${value}"
      return
    fi
  fi
  echo "${default}"
}

HOUR="$(read_env_var EVENTS_SCHEDULE_HOUR 19)"
MINUTE="$(read_env_var EVENTS_SCHEDULE_MINUTE 0)"
RUN_SCRIPT="${SCRIPT_DIR}/run_events_job.sh"

cat <<EOF
# Adicione ao crontab (crontab -e), após a linha do radar diário:
CRON_TZ=America/Sao_Paulo
${MINUTE} ${HOUR} * * * ${RUN_SCRIPT}
EOF
