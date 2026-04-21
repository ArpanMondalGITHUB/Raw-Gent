FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=2.1.3

WORKDIR /app

RUN groupadd --system appuser && useradd --system --gid appuser --create-home appuser

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

COPY . .
RUN chown -R appuser:appuser /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import sys, urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3); sys.exit(0)"

USER appuser

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
