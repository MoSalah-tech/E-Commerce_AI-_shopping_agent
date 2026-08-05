FROM python:3.11-slim

WORKDIR /app

# System deps needed for psycopg (PostgreSQL) to build/run correctly
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (separate layer -- speeds up rebuilds when
# only app code changes, since this layer gets cached).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app
COPY . .

# Most container platforms (Render, Back4app, etc.) inject a PORT env var
# and expect the app to bind to it -- default to 8000 for local testing.
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]