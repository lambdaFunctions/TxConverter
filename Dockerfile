ARG PYTHON_VERSION=3.10.16

# ── stage 1: builder (shared base for test + runtime) ────────────────────────
FROM public.ecr.aws/docker/library/python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-cache --no-root --only main

# ── stage 2: test (CI only — never pushed to ECR) ────────────────────────────
FROM builder AS test

ENV PATH="/app/.venv/bin:$PATH"

RUN poetry install --no-interaction --no-cache --no-root

COPY . .

ENV APP_ENV=test

CMD ["python", "-m", "pytest", "tests/", "-v", "--no-header", "--tb=short", "--cov=src/txconverter", "--cov-report=term-missing"]

# ── stage 3: runtime (production image) ──────────────────────────────────────
FROM public.ecr.aws/docker/library/python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv

COPY src/ ./src/
COPY infra/ ./infra/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN useradd --no-create-home --shell /bin/false appuser && \
    mkdir -p /data && chown appuser:appuser /app /data

VOLUME ["/data"]

USER appuser

ENTRYPOINT ["/entrypoint.sh"]
