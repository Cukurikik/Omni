#=============================================================================
# OMNI INFRASTRUCTURE LAYER — SWARM AGENT CONTAINER (DOCKER)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Isolated Docker container definition for individual Swarm Agents.
#              While Unikernels are preferred, Docker provides legacy support.
#=============================================================================

FROM ubuntu:24.04 AS builder

# Install OMNI Framework Dependencies
RUN apt-get update && apt-get install -y \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install OMNI CLI
RUN curl -sSL https://nexus.omniframework.dev/install.sh | bash

WORKDIR /app
COPY Omnifile.toml .
COPY src/ src/

# Build the specific Swarm Agent target via Omni Universal Compiler
RUN omni build --target linux-x64 --profile release-swarm

# Runtime Stage
FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /app/build/omni-swarm-agent .

# Environment configuration
ENV OMNI_ENV=production
ENV SWARM_MODE=isolated

# Run the statically linked binary
CMD ["./omni-swarm-agent", "--start"]
