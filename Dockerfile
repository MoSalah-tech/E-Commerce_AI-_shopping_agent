FROM python:3.11-slim

WORKDIR /app

# System deps needed for psycopg (PostgreSQL) to build/run correctly
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv itself
RUN pip install --no-cache-dir uv

# Install deps first (separate layer -- cached unless pyproject.toml/uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Now copy the rest of the app
COPY app ./app

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]