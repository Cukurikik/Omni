# Omni Libre Chat (Dockerfile)
# Infrastructure Layer: Immutable container for self-hosted chat.
# Ref: vemonet/libre-chat

FROM python:3.11-slim AS base
WORKDIR /omni/libre-chat
RUN pip install --no-cache-dir fastapi uvicorn
COPY . /omni/libre-chat/
USER nobody
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
