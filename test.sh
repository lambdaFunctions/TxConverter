#!/usr/bin/env bash
set -euo pipefail

IMAGE="${IMAGE:-txconverter}"

echo "==> Running tests in Docker"
echo "────────────────────────────────────────────────────────────────────────"

set +e
docker run --rm "${IMAGE}:test"
TEST_EXIT=$?
set -e

echo "────────────────────────────────────────────────────────────────────────"

if [ "${TEST_EXIT}" -ne 0 ]; then
    echo ""
    echo "FAILED: tests exited with code ${TEST_EXIT}."
    exit "${TEST_EXIT}"
fi

echo ""
echo "PASSED: all tests green."
