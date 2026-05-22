#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE="${IMAGE:-txconverter}"
GIT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"
TAG="${TAG:-${GIT_SHA}}"
CONTAINER="${CONTAINER:-txconverter}"
PORT="${PORT:-8000}"

bash "${DIR}/test.sh"

echo ""
echo "==> Starting container '${CONTAINER}' on port ${PORT}"
docker rm -f "${CONTAINER}" 2>/dev/null || true

docker run \
    --detach \
    --name "${CONTAINER}" \
    --publish "${PORT}:8000" \
    --env APP_ENV=prod \
    --volume txconverter-data:/data \
    "${IMAGE}:${TAG}"

echo "Container '${CONTAINER}' is running. Streaming logs (Ctrl-C stops the log tail, not the container):"
echo ""
docker logs --follow "${CONTAINER}"
