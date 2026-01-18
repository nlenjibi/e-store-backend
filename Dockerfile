# Multi-stage Dockerfile for Django E-Commerce Backend
# Production-ready with Python 3.11, Gunicorn, PostgreSQL, and Redis

# ========================================
# Stage 1: Builder - Install dependencies
# ========================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# ========================================
# Stage 2: Runtime - Production image
# ========================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /root/.local

# Copy project files
COPY --chown=appuser:appuser . .

# Create directories for static and media files
RUN mkdir -p staticfiles media logs && \
    chown -R appuser:appuser staticfiles media logs

# Switch to non-root user
USER appuser

# Collect static files (will be overridden by volume in docker-compose if needed)
RUN python manage.py collectstatic --noinput --clear || true

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/admin/login/', timeout=2)" || exit 1

# Default command (can be overridden in docker-compose.yml)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
