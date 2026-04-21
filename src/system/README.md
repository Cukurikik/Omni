# OMNI System Layer Engines

This directory contains **bare-metal, memory-critical engines** written in languages that provide
direct hardware access and zero-cost abstractions.

## Supported Languages
| Language | Idiom | Use Case |
|----------|-------|----------|
| **C** | `extern "omni-c" fn` | Bare-metal I/O, FFI binding, kernel interface |
| **C++** | `@cpp_template<T>` | Template metaprogramming, RAII, GPU compute |
| **Rust** | `own<T>`, `borrow<T>` | Memory-safe concurrency, ownership model |
| **Zig** | `zig::comptime` | No-undefined-behavior system programming |
| **Carbon** | `carbon::interface` | Modern C++ successor |

## Engines
| File | Source Repo | Purpose |
|------|-------------|---------|
| `about_attack_redteam.c` | About-Attack | Red Team memory payload simulation |
| `cheatengine_mcp_memory.c` | cheatengine-mcp-bridge | Ring-0 pointer chain resolver & RTTI |
| `claw_agent_harness.rs` | claw-codes | Memory-safe AI agent runtime harness |
| `cpp_reflection_engine.cpp` | CPP-Reflection | Runtime C++ type introspection |
| `dockflare_tunnel.rs` | DockFlare | Cloudflare tunnel proxy via Docker socket |
| `flow_like_engine.carbon` | flow-like | NextGen C++-safe visual workflow engine |
| `keymapper_kernel.zig` | Keymapper | Kernel-level input remapping mutator |
| `lossless_switcher.cpp` | LosslessSwitcher | OS audio stream interception |
| `masterparser_logs.rs` | MasterParser | Forensic log parser with structured output |
| `memory_manager.rs` | OMNI Core | Foundation memory management primitives |
| `tlsfuzzer_engine.zig` | tlsfuzzer | Memory-safe malformed TLS packet generator |
