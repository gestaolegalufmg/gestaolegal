FROM python:3.11.3-buster

COPY --from=ghcr.io/astral-sh/uv:0.7.17 /uv /uvx /bin/

WORKDIR /code

COPY ./pyproject.toml /code
COPY ./uv.lock /code
COPY . /code

RUN uv sync --locked --no-dev

ENV PATH="/code/.venv/bin:$PATH"

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=4", "--timeout=300", "gestaolegal.wsgi:app"]
