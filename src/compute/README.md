# OMNI Compute Layer Engines

This directory contains **compute-intensive, data-science, and ML/AI engines** for
numerical computing, statistical modelling, and high-performance processing.

## Supported Languages
| Language | Idiom | Use Case |
|----------|-------|----------|
| **Python** | `py::` | ML pipeline, data wrangling, scripting |
| **Julia** | `@julia_simd` | SIMD vector ops, numerical computing, HPC |
| **R** | `r::stat` | Statistical modelling, probabilistic inference |
| **Mojo** | `mojo::accelerate` | AI-first, Python-compatible high perf |
| **Haskell** | `hs::pure` | Pure functional, formal verification |

## Native Engines (Non-Python)
| File | Source Repo | Purpose |
|------|-------------|---------|
| `agent_farm_orchestrator.mojo` | claude_code_agent_farm | AI agent cluster orchestation |
| `claude_marketplace_skills.py` | claude-skills-marketplace | Local AI skill execution sandbox |
| `ClashIpChecker.hs` | clash-ip-checker | Pure functional IP validator |
| `ffmpeg_encoder_stats.r` | FFmpeg Tools | Encoder statistics & optimization |
| `google_it_automation.R` | google-it-automation | IT-ops statistical process auditor |
| `nexrender_core.jl` | Nexrender | HPC data automation engine |
| `nussknacker_engine.jl` | Nussknacker | Real-time compute stream rules |
| `pipelex_ai_methods.py` | Pipelex | Typed AI procedural pipeline |
| `proctoring_ai_engine.R` | Proctoring-AI | Gaze/facial anomaly detection |

## Python Core Engines
Located in `python_core/` — these are the original Semester 1–2 Python engines
plus Semester 3 Batch 1–3 engines. See `python_core/` for full listing.
