#!/usr/bin/env bash
set -euo pipefail

export APP_ENV="${APP_ENV:-local}"

APP_MODULE="${APP_MODULE:-src.txconverter.main:app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-$(nproc)}"

echo "Starting uvicorn with $WORKERS workers on $HOST:$PORT"

exec uvicorn "$APP_MODULE" \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --proxy-headers \
    --forwarded-allow-ips '*'
