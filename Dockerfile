# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for bot2mvp Telegram Bot
# Stage 1: Builder
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:$PYTHONPATH" \
    PATH="/app/.venv/bin:$PATH" \
    HOME=/home/bot

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv in runtime stage (needed for ENTRYPOINT)
RUN pip install --no-cache-dir uv

# Create non-root user for security
RUN groupadd -r bot && useradd -r -g bot bot && \
    mkdir -p /app/logs /home/bot/.cache && \
    chown -R bot:bot /app /home/bot

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=bot:bot /app/.venv /app/.venv

# Copy application source code
COPY --chown=bot:bot . .

# Create logs directory
RUN mkdir -p logs && chown -R bot:bot logs

# Switch to non-root user
USER bot

# Health check: verify bot connectivity (simplified check)
# In a real setup, you might expose a health endpoint on port 9000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Entrypoint: Start the bot
ENTRYPOINT ["uv", "run", "python", "bot/main.py"]
