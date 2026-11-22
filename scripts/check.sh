#!/usr/bin/env bash
set -euo pipefail

echo "[check] Step 1/2: Running unit tests with pytest..."
pytest -q

if [[ "${1:-}" == "--live" ]]; then
  echo "[check] Step 2/2: Checking live health endpoint at http://localhost:8080/health..."
  curl -fsS http://localhost:8080/health >/dev/null
  echo "[check] Live /health check passed."
fi

echo "[check] SUCCESS: All checks passed."
