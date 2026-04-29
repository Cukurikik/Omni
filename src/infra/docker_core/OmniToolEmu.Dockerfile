# Omni ToolEmu (Dockerfile)
# Infrastructure Layer: Immutable container definition for the ToolEmu evaluator sandbox.

FROM alpine:3.19 AS base

# Install strict dependencies
RUN apk add --no-cache nodejs tzdata

# Set working directory
WORKDIR /omni/toolemu

# Copy pre-compiled engine (assuming pre-compiled via Omni Builder)
COPY ./bin/omni_toolemu_evaluator.js /omni/toolemu/

# Lock permissions strictly
RUN chown -R root:root /omni/toolemu && \
    chmod 555 /omni/toolemu/omni_toolemu_evaluator.js

USER guest

# Entrypoint enforces strict mode execution
ENTRYPOINT ["node", "--use-strict", "/omni/toolemu/omni_toolemu_evaluator.js"]
