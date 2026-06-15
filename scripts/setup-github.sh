#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_NAME="${1:-radar-financeiro-ia}"

cd "${PROJECT_DIR}"

if git diff --cached --name-only 2>/dev/null | grep -qx '.env'; then
  echo "ERRO: .env está no staging. Abortando." >&2
  exit 1
fi

if [[ ! -d .git ]]; then
  git init
  git checkout -b main
fi

git add -A

if git diff --cached --name-only | grep -qx '.env'; then
  echo "ERRO: .env entrou no staging após git add. Verifique .gitignore." >&2
  git reset HEAD .env 2>/dev/null || true
  exit 1
fi

echo "Arquivos a commitar:"
GIT_PAGER=cat git diff --cached --name-only

if ! git rev-parse HEAD >/dev/null 2>&1; then
  git commit -m "$(cat <<'EOF'
MVP 1: radar diário com coleta, IA, Telegram e operação local.

Coleta BRAPI, destaques de preço, resumo Gemini, envio Telegram,
API REST, testes, cron e documentação do backlog.
EOF
)"
elif ! git diff --cached --quiet; then
  git commit -m "MVP 1: radar diário com coleta, IA, Telegram e operação local."
else
  echo "Nada novo para commitar."
fi

if ! gh auth status >/dev/null 2>&1; then
  echo ""
  echo "GitHub CLI não autenticado. Rode: gh auth login"
  echo "Depois: gh repo create ${REPO_NAME} --public --source=. --remote=origin --push"
  exit 0
fi

BRANCH="$(git branch --show-current 2>/dev/null || echo main)"

if gh repo view "${REPO_NAME}" >/dev/null 2>&1; then
  echo "Repositório ${REPO_NAME} já existe. Fazendo push..."
  git remote add origin "https://github.com/$(gh api user -q .login)/${REPO_NAME}.git" 2>/dev/null \
    || git remote set-url origin "https://github.com/$(gh api user -q .login)/${REPO_NAME}.git"
  git push -u origin "${BRANCH}"
else
  gh repo create "${REPO_NAME}" --public --source=. --remote=origin --push
fi

echo ""
echo "Pronto: https://github.com/$(gh api user -q .login)/${REPO_NAME}"
