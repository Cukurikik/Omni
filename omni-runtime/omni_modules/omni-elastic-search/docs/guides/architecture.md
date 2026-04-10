# omni-elastic-search - Architecture Guide

## Layer Structure
src/
  system/   - Rust/C/C++ (drivers, memory, crypto, I/O)
  network/  - Go (connections, protocols, HTTP, gRPC)
  domain/   - C#/GraphQL (business logic, types, validation)
  compute/  - Python/Julia/R (pipelines, analytics, ML)
  ui/       - TypeScript (SDK, types, reactive state)

## Data Flow
UI -> Network -> Domain -> Compute -> System (and back)

## Zero-Copy Principle
All cross-layer data transfer uses pointer references, not copies.