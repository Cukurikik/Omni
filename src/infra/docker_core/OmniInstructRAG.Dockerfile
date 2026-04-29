# Omni InstructRAG Container (Dockerfile)
# Ref: weizhepei/InstructRAG — ICLR 2025
FROM python:3.11-slim AS base
WORKDIR /omni/instructrag
RUN pip install --no-cache-dir transformers datasets
COPY . /omni/instructrag/
USER nobody
ENTRYPOINT ["python", "-m", "omni.instructrag.server"]
