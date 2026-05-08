#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/sd-dj-ramjaap2-pro}"
BRANCH="${BRANCH:-main}"

echo "==> Deploying from ${APP_DIR} on branch ${BRANCH}"

cd "${APP_DIR}"

if [ ! -d ".git" ]; then
  echo "Error: ${APP_DIR} is not a git repository."
  exit 1
fi

if [ ! -f ".env.docker" ]; then
  echo "Error: .env.docker not found."
  echo "Run: cp .env.docker.example .env.docker && nano .env.docker"
  exit 1
fi

echo "==> Fetching latest code"
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --rebase origin "${BRANCH}"

echo "==> Rebuilding and restarting Docker services"
docker compose down
docker compose up --build -d

echo "==> Service status"
docker compose ps

echo "==> Last 50 lines of web logs"
docker compose logs --tail=50 web

echo "==> Deployment complete"
