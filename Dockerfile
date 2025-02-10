# syntax=docker/dockerfile:1
FROM --platform=$TARGETPLATFORM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Build wheels for numpy and pandas first
COPY requirements.txt .
RUN pip wheel --no-deps --no-cache-dir numpy==1.24.3 pandas==2.0.3

FROM --platform=$TARGETPLATFORM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libpq5 \
    libopenjp2-7 \
    libtiff6 \
    libatlas-base-dev \
    libwebp7 \
    libgstreamer1.0-0 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install pre-built wheels
COPY --from=builder /app/*.whl /app/
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install *.whl \
    && pip install -r requirements.txt

COPY . .

RUN chmod +x /app/scripts/entrypoint.sh

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]