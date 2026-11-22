#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-1.0}"
IMAGE="docketlite:${TAG}"
CONTAINER_NAME="docketlite"

echo "[deploy] Deploying ${IMAGE}..."
docker image inspect "${IMAGE}" >/dev/null

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker stop "${CONTAINER_NAME}" >/dev/null
  docker rm "${CONTAINER_NAME}" >/dev/null
fi

docker run -d --name "${CONTAINER_NAME}" --restart unless-stopped -p 8080:8080 "${IMAGE}" >/dev/null
sleep 3
docker ps --filter "name=${CONTAINER_NAME}"
echo "[deploy] Deployed ${IMAGE} cleanly."
