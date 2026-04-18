# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# A Dockerfile describes how to build a Docker container image for our app.
# A container is like a lightweight virtual machine that packages our app
# with all its dependencies, so it runs identically on any machine or cloud.
#
# WHY MULTI-STAGE BUILD?
#   Stage 1 (builder): Installs all build tools and dependencies — this stage
#     can be large because it needs compilers, headers, etc.
#   Stage 2 (runtime): Copies only the installed packages from the builder.
#     The final image is much smaller (no build tools = smaller attack surface).
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Use the official Python slim image as the base — "slim" means no extras
FROM python:3.11-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# WHY COPY requirements.txt FIRST?
#   Docker layers are cached. If requirements.txt hasn't changed,
#   Docker skips the pip install step on the next build — much faster!
COPY requirements.txt .

# Install Python dependencies into a specific directory for easy copying
# --no-cache-dir: Don't save pip's download cache (saves ~100MB in image)
# --prefix: Install to /install so we can copy just this folder to the runtime stage
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security best practice: never run as root inside a container.
# If an attacker breaks into the container, they get limited permissions.
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy the installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ ./app/

# Copy sample documents for initial indexing
COPY data/ ./data/

# Create the ChromaDB data directory and set permissions
# This is where ChromaDB will persist its vector data
RUN mkdir -p /app/chroma_data && chown -R appuser:appuser /app

# Switch to non-root user for all subsequent commands
USER appuser

# Expose the application port (must match APP_PORT env var)
EXPOSE 8000

# Health check: Docker/Azure will call this to verify the container is healthy
# --interval: Check every 30 seconds
# --timeout:  Consider unhealthy if no response in 10 seconds
# --retries:  Mark unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# The command to start the server
# --host 0.0.0.0: Listen on all network interfaces (required inside containers)
# --workers 1:    Single worker (use Azure scaling instead of multiple workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
