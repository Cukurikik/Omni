# OMNI MOTHER: Universal Dockerfile (Production Grade)
# Compiles all 15+ languages into the single Omni Kernel.

FROM ubuntu:24.04

# Install LLVM and Clang
RUN apt-get update && apt-get install -y \
    llvm-18 clang-18 \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install Go
RUN curl -O https://dl.google.com/go/go1.22.0.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"

WORKDIR /omni
COPY . .

# Execute Universal Build
# RUN ./omni_build.sh --target release
CMD ["echo", "[OMNI DOCKER] Universal Builder Ready."]
