#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8080}"
echo "waiting for ${BASE_URL}/sc/health ..."
for i in $(seq 1 90); do
  if curl -sf "${BASE_URL}/sc/health" >/dev/null; then
    echo "healthy after ${i}s"
    curl -sf "${BASE_URL}/sc/health" | head -c 400
    echo
    exit 0
  fi
  sleep 1
done
echo "ERROR: health check timed out" >&2
exit 1
