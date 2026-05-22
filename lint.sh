#!/usr/bin/env bash
set -euo pipefail

echo "==> Running ruff check (auto-fix)..."
poetry run ruff check --fix .

echo "==> Running ruff format..."
poetry run ruff format .

echo "==> Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "Done."
