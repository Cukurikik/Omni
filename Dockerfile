# OMNI Divine Core - Multi-Stage Universal Build
FROM omni-nexus-core:latest AS builder
WORKDIR /app

# Copy Omnifile and layer dependencies
COPY Omnifile.toml .
COPY src/ bridge/ ./src/

# Compile the Universal Binary for cloud deployment (Unikernel target if supported, falling back to Linux binary)
RUN omni build --release --target x86_64-linux

# Production Stage
FROM alpine:latest
WORKDIR /opt/omni

# Install physical layer bridges if necessary
RUN apk add --no-cache libgcc libstdc++ ca-certificates

# Copy from builder
COPY --from=builder /app/target/x86_64-linux/release/omni-nexus-core /usr/local/bin/omni-nexus

# Enforce secure permissions
RUN chmod +x /usr/local/bin/omni-nexus && adduser -D omni_deity
USER omni_deity

# Expose standard Omni network protocol ports
EXPOSE 8080 9090

ENTRYPOINT ["omni-nexus", "--mode", "production"]
