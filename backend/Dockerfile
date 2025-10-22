# ==============================================================================
# Dockerfile for LangChain Mini-RAG API
# ==============================================================================
# This Dockerfile creates a production-ready container for the RAG API.
# It uses multi-stage builds and best practices for security and performance.
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Builder
# ------------------------------------------------------------------------------
# We use a builder stage to install dependencies separately from the runtime.
# This allows us to use a full Python image for building, then copy only
# what we need to a slim runtime image.

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
# - build-essential: C compiler for packages with C extensions
# - curl: For health checks and downloads
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
# Docker caches layers, so if requirements.txt doesn't change,
# this layer is reused and pip install is skipped
COPY requirements.txt .

# Install Python dependencies to a local directory
# --user flag installs to /root/.local instead of system-wide
# --no-cache-dir reduces image size by not keeping pip cache
RUN pip install --user --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Runtime
# ------------------------------------------------------------------------------
# This is the final image that will be used to run the application.
# It's based on a slim Python image to minimize size.

FROM python:3.11-slim

# Set metadata labels (good practice for image documentation)
LABEL maintainer="Euxhenjo Nexhipi <euxhenjonex.com>"
LABEL description="LangChain Mini-RAG API - Retrieval Augmented Generation with FastAPI"
LABEL version="1.0"

# Set environment variables
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # PATH: Add local pip packages to PATH
    PATH=/root/.local/bin:$PATH \
    # Set default port
    PORT=8000

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
# Running as root in containers is a security risk
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy installed Python packages from builder stage
# This avoids having build tools in the final image
COPY --from=builder /root/.local /root/.local

# Copy application code
# Copy as root first, then change ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose the port the app runs on
# This is documentation; actual port mapping happens at runtime
EXPOSE ${PORT}

# Health check
# Docker will periodically run this command to check if container is healthy
# If health checks fail multiple times, Docker can restart the container
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Default command to run the application
# Uses uvicorn with production settings:
# --host 0.0.0.0: Listen on all network interfaces (required for Docker)
# --port ${PORT}: Use PORT env var (default 8000)
# --workers 1: Single worker (can be increased for production)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

# ==============================================================================
# Build and Run Instructions:
# ==============================================================================
#
# Build the image:
#   docker build -t langchain-rag-api:latest .
#
# Run the container:
#   docker run -d \
#     --name rag-api \
#     -p 8000:8000 \
#     -e OPENAI_API_KEY=your_key_here \
#     langchain-rag-api:latest
#
# Run with custom port:
#   docker run -d \
#     --name rag-api \
#     -p 9000:9000 \
#     -e PORT=9000 \
#     -e OPENAI_API_KEY=your_key_here \
#     langchain-rag-api:latest
#
# Run with .env file:
#   docker run -d \
#     --name rag-api \
#     -p 8000:8000 \
#     --env-file .env \
#     langchain-rag-api:latest
#
# View logs:
#   docker logs -f rag-api
#
# Stop container:
#   docker stop rag-api
#
# Remove container:
#   docker rm rag-api
#
# ==============================================================================
