# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Set workdir for all stages
WORKDIR /app

# --- Builder stage: install dependencies and create venv ---
FROM base AS builder

# Copy only requirements.txt if present, else fallback to pip freeze
# (Assume requirements.txt is present in ./referee or fallback to none)
# If you have requirements.txt, uncomment the next two lines and adjust as needed:
# COPY --link requirements.txt ./
# RUN --mount=type=cache,target=/root/.cache/pip python -m venv .venv && .venv/bin/pip install -r requirements.txt

# If no requirements.txt, just create venv and install nothing
RUN --mount=type=cache,target=/root/.cache/pip python -m venv .venv

# Copy the application code (referee module)
COPY --link . .

# --- Final stage: minimal runtime image ---
FROM base AS final

# Create non-root user
RUN adduser --disabled-password --gecos '' refereeuser

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code from builder
COPY --from=builder /app /app

# Set environment so venv is used
ENV PATH="/app/.venv/bin:$PATH"

USER refereeuser

# Default entrypoint: run the referee module
ENTRYPOINT ["python", "-m", "referee"]
