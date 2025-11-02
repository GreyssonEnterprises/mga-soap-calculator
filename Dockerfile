# Multi-stage build for production-grade FastAPI application
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY pyproject.toml ./

# Install dependencies in a virtual environment
RUN python -m pip install --upgrade pip && \
    python -m pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels -e .


# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy wheels from builder
COPY --from=builder /tmp/wheels /wheels
COPY --from=builder /tmp/pyproject.toml ./

# Install wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser migrations ./migrations
COPY --chown=appuser:appuser scripts ./scripts
COPY --chown=appuser:appuser .env.example ./

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
