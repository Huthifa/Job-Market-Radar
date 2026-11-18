# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create an isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Point PATH to the copied virtual environment
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy only the pre-built virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY ./api ./api

EXPOSE 8000

CMD ["fastapi", "run", "api/main.py", "--port", "8000"]
