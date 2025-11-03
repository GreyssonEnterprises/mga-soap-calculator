# Multi-stage build for MGA SOAP Calculator API
# Using Red Hat Universal Base Image (UBI) 9 for enterprise deployment
# Target: Fedora 42 with Podman, PostgreSQL 15

# ==============================================================================
# Stage 1: Builder - Compile dependencies and create wheels
# ==============================================================================
FROM registry.access.redhat.com/ubi9/python-311:latest AS builder

# Set build-time environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Switch to root for package installation
USER 0

# Install build dependencies
# UBI 9 uses dnf instead of apt
RUN dnf install -y \
    gcc \
    gcc-c++ \
    postgresql-devel \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Create build directory
WORKDIR /build

# Copy dependency files
COPY pyproject.toml README.md ./

# Build wheels for all dependencies
# This creates portable binary packages that don't need compilation at runtime
RUN python3.11 -m pip install --upgrade pip setuptools wheel && \
    python3.11 -m pip wheel --no-cache-dir --wheel-dir /wheels -e .

# ==============================================================================
# Stage 2: Runtime - Minimal production image
# ==============================================================================
FROM registry.access.redhat.com/ubi9/python-311:latest

# Metadata labels (OpenContainer Initiative format)
LABEL name="mga-soap-calculator-api" \
      vendor="MGA Automotive" \
      version="1.0.0" \
      summary="Core Soap Calculation API with additive effect modeling" \
      description="FastAPI application for soap formulation calculations with PostgreSQL backend" \
      maintainer="info@mga-automotive.com"

# Runtime environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/app-root/bin:${PATH}" \
    APP_ROOT=/opt/app-root/src

# Switch to root for runtime dependencies
USER 0

# Install runtime dependencies only (no build tools)
RUN dnf install -y \
    postgresql-libs \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# UBI images come with default user 1001
# Ensure proper ownership of application directory
RUN chown -R 1001:0 ${APP_ROOT} && \
    chmod -R g=u ${APP_ROOT}

# Set working directory
WORKDIR ${APP_ROOT}

# Copy wheels from builder stage
COPY --from=builder /wheels /tmp/wheels

# Install pre-built wheels
RUN python3.11 -m pip install --no-cache-dir /tmp/wheels/*.whl && \
    rm -rf /tmp/wheels

# Copy application code with proper ownership
# UBI standard: user 1001, group 0 (root group for OpenShift compatibility)
COPY --chown=1001:0 app ./app
COPY --chown=1001:0 migrations ./migrations
COPY --chown=1001:0 scripts ./scripts
COPY --chown=1001:0 alembic.ini ./
COPY --chown=1001:0 .env.example ./

# Ensure execute permissions on scripts
RUN chmod -R g+rx scripts/ && \
    chmod g+r alembic.ini .env.example

# Switch to non-root user (UBI standard UID 1001)
# This user exists by default in UBI Python images
USER 1001

# Health check endpoint
# Uses Python instead of curl to avoid extra dependencies
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3.11 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health').read()" || exit 1

# Expose API port
EXPOSE 8000

# Production server command
# Using uvicorn with production-grade workers
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--access-log", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
