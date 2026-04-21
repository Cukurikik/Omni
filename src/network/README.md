# OMNI Network Layer Engines

This directory contains **concurrency-first, I/O-optimized engines** built for high-throughput
networking, event-driven processing, and fault-tolerant distributed systems.

## Supported Languages
| Language | Idiom | Use Case |
|----------|-------|----------|
| **Go** | `spawn goroutine` | Green threads, channel-based CSP, HTTP servers |
| **JavaScript** | `async evloop` | Event loop, non-blocking I/O, browser runtime |
| **Elixir** | `elixir::spawn_link` | Actor model, fault tolerance, soft-realtime |

## Engines
| File | Source Repo | Purpose |
|------|-------------|---------|
| `browserless_worker.js` | Browserless | Headless browser pool manager |
| `ffmate_cluster.ex` | FFmate | Distributed FFmpeg transcoding actors |
| `figma_mcp_bridge.go` | figma-mcp-go | MCP STDIO bridge to Figma API |
| `gateway.go` | OMNI Core | Root network gateway router |
| `omni_nginx_le_proxy.js` | nginx-le | TLS/SSL proxy multiplexing |
| `opendia_mcp.go` | Opendia | MCP WebSocket tunnel server |
| `puppeteer_replay_actor.ex` | Puppeteer Replay | Actor-based browser replay concurrency |
| `shuffle_soar.go` | Shuffle SOAR | Security orchestration pipeline |
| `spacebot_core.go` | SpaceBot | Community management agent harness |
| `steam_idler_service.go` | steam-game-idler | Concurrent game idle session manager |
| `syncd_deploy.go` | Syncd | Code deployment synchronization |
| `tiktok_uploader.go` | tiktok-uploader | Multi-thread async upload automation |
| `whatsapp_automator.js` | PyWhatsapp | Async WhatsApp messaging event loop |
