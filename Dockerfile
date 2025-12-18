# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

# Install system dependencies (cron, tzdata)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

# Copy application code and scripts
COPY . /app

# Create volume mount points
RUN mkdir -p /data /cron && \
    chmod 755 /data /cron

# Install cron configuration
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Expose API port
EXPOSE 8080

# Start cron and API server
CMD ["sh", "-c", "service cron start && uvicorn main:app --host 0.0.0.0 --port 8080"]

