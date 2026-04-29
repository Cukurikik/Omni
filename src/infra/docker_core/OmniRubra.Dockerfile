# Omni Rubra Container (Dockerfile)
# Ref: rubra-ai/rubra
FROM python:3.11-slim AS base
WORKDIR /omni/rubra
RUN pip install --no-cache-dir vllm transformers
COPY . /omni/rubra/
USER nobody
ENTRYPOINT ["python", "-m", "vllm.entrypoints.openai.api_server"]
