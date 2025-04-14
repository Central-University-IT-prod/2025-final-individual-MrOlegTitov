FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# UV installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# UV project copy
COPY pyproject.toml .
COPY uv.lock .


FROM base AS api
RUN uv sync --frozen --group api

COPY adsplatform adsplatform

CMD ["uvicorn", "adsplatform.api.main:app", "--host", "REDACTED", "--port", "8080"]


FROM base AS bot
RUN uv sync --frozen --group bot

COPY adsplatform adsplatform

CMD ["python", "-m", "adsplatform.bot.main"]


FROM base AS tests
RUN uv sync --frozen --group tests

COPY tests tests
COPY adsplatform adsplatform

CMD ["uv", "run", "pytest", "tests/e2e", "tests/unit"]
