# See: https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile

FROM python:3.11.3-alpine AS base

COPY --from=ghcr.io/astral-sh/uv:0.7.17 /uv /uvx /bin/

WORKDIR /code

ENV UV_LINK_MODE=copy

# Development stage
FROM base AS dev

ENV UV_COMPILE_BYTECODE=0
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /code

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/code/.venv/bin:$PATH"

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]

# Production stage
FROM base AS prod

ENV UV_COMPILE_BYTECODE=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /code

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/code/.venv/bin:$PATH"

ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "gestaolegal:create_app()"]
