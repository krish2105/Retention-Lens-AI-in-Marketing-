# RetentionLens API (FastAPI) plus the ML package used by the scoring worker.
# Build: docker build -t retentionlens-api .   Run: docker run -p 8000:8000 --env-file .env retentionlens-api
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    RL_ML_CMD="python -m retentionlens.ingest" \
    RL_SERVING_DIR=/app/apps/web/public/data \
    RL_STATE_DB=/data/retentionlens.sqlite3 \
    RL_DATA_DIR=/data/orgs \
    RL_AUTH_MODE=local \
    RL_COOKIE_SECURE=1

WORKDIR /app
COPY ml/pyproject.toml ml/pyproject.toml
COPY ml/retentionlens ml/retentionlens
COPY services/api/requirements.txt services/api/requirements.txt
RUN pip install ./ml -r services/api/requirements.txt \
    && useradd --create-home --uid 10001 app && mkdir -p /data && chown app /data
COPY services/api/app services/api/app
# Reference (sample) dataset: the same exported JSON the public demo uses.
COPY apps/web/public/data apps/web/public/data

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["sh", "-c", "uvicorn app.main:app --app-dir services/api --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
