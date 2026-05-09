# OMNI Framework - Dockerfile for Liputan6 Summarizer Service
FROM python:3.10-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final runtime image
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY src/compute/python/omni_indo_summarizer.py /app/main.py
COPY models/ /app/models/

EXPOSE 8000
CMD ["python", "main.py", "--serve"]
