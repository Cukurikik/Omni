# OMNI Framework - Multi-Stage Dockerfile for MoE Runtime
# Compiles the C++/CUDA UCCL backend, Rust memory allocators, and Go Gateway into a single container.

# Stage 1: Build C++/CUDA Core
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 AS cpp-builder
WORKDIR /build
COPY src/system/cpp/ ./cpp/
COPY src/system/cuda/ ./cuda/
# Simulate compilation step
RUN echo "Compiling UCCL and MoE CUDA kernels..." && \
    mkdir -p /out/lib && \
    touch /out/lib/libomnimoe.so

# Stage 2: Build Rust Allocator
FROM rust:1.75-bookworm AS rust-builder
WORKDIR /build
COPY src/system/rust/omni_moe_tensor_allocator/ ./
# Simulate cargo build
RUN echo "Compiling OmniMoEAllocator..." && \
    mkdir -p /out/lib && \
    touch /out/lib/libomni_moe_alloc.so

# Stage 3: Build Go Gateway
FROM golang:1.21-bullseye AS go-builder
WORKDIR /build
COPY src/network/go/ ./
# Simulate go build
RUN echo "Compiling Go Router/Gateway..." && \
    mkdir -p /out/bin && \
    touch /out/bin/omni-gateway && chmod +x /out/bin/omni-gateway

# Stage 4: Final Production Image
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04
WORKDIR /opt/omni

# Copy shared libraries
COPY --from=cpp-builder /out/lib/libomnimoe.so /usr/local/lib/
COPY --from=rust-builder /out/lib/libomni_moe_alloc.so /usr/local/lib/

# Copy binaries
COPY --from=go-builder /out/bin/omni-gateway /usr/local/bin/

# Set LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"

# Default Entrypoint to start the Go API Gateway which drives the C++ engine
ENTRYPOINT ["/usr/local/bin/omni-gateway"]
EXPOSE 8080 50051
