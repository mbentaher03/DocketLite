#!/usr/bin/env bash
set -euo pipefail
TAG="${1:?usage: ./scripts/deploy.sh vX.Y.Z}"
echo "IMAGE_TAG=${TAG}" > .env.deploy
COMPOSE=(docker compose --env-file .env.deploy -f compose.staging.yaml)echo "[deploy] Pulling ${TAG}..."
"${COMPOSE[@]}" pull
"${COMPOSE[@]}" up -d
echo "[deploy] Waiting for /health..."
for i in $(seq 1 30); do
  if curl -fsS http://localhost:8080/health >/dev/null 2>&1; then
    echo "[deploy] ${TAG} is healthy:"
    curl -fsS http://localhost:8080/version; echo
    exit 0
  fi
  sleep 2
done
echo "[deploy] ${TAG} is NOT healthy. Last logs:"
"${COMPOSE[@]}" logs --tail=50 api
exit 1
