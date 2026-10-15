# Build from the repo root: docker build -f backend/Dockerfile .
# (docker-compose.yml at the repo root already sets this context)
FROM python:3.12-slim

WORKDIR /app

# no apt-get needed here: psycopg2-binary ships a precompiled manylinux wheel
# with libpq bundled in, so there's nothing to compile and no system libs
# to install - one less thing that can fail on a slow/restricted network
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app ./backend/app
COPY models ./models
COPY data/processed ./data/processed
COPY rag/embeddings ./rag/embeddings

WORKDIR /app/backend
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
