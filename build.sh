#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-txconverter}"
GIT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"
TAG="${TAG:-${GIT_SHA}}"

echo "==> [1/2] Building test image"
docker build \
  --target test \
  --tag "${IMAGE}:test" \
  .

echo ""
echo "==> [2/2] Building runtime image"
docker build \
  --target runtime \
  --tag "${IMAGE}:${TAG}" \
  --tag "${IMAGE}:latest" \
  .

echo ""
echo "Built:"
echo "  ${IMAGE}:test"
echo "  ${IMAGE}:${TAG}"
echo "  ${IMAGE}:latest"
