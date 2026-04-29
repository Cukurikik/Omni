#!/bin/bash
# Omni WKM Bootstrap (Bash)
# System Layer: Deterministic startup for World Knowledge Model agent.
# Ref: zjunlp/WKM

set -euo pipefail
echo "[OMNI] Initializing WKM Agent Planner..."
export OMNI_WKM_MAX_DEPTH=10
export OMNI_WKM_KB_PATH="${OMNI_WKM_KB_PATH:-/data/wkm/kb.json}"
if [ ! -f "$OMNI_WKM_KB_PATH" ]; then
    echo "[OMNI_FATAL] Knowledge base not found at $OMNI_WKM_KB_PATH"
    exit 1
fi
echo "[OMNI] WKM Engine Ready. Max Depth: $OMNI_WKM_MAX_DEPTH"
