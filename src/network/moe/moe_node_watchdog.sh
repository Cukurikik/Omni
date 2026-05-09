#!/bin/bash
# moe_node_watchdog.sh — Network / Observability
# Layer: Network / Infra — Node Health Watchdog
#
# A fast shell-based watchdog that continuously pings physical GPU nodes
# in the cluster. If a node fails to respond, it triggers an alert to the Go Gateway
# to immediately stop routing tokens to that node's experts.

set -e

# Zero-mock configuration
GATEWAY_URL="http://localhost:8080/api/nodes"
declare -a NODE_IPS=("10.0.0.10" "10.0.0.11" "10.0.0.12")
TIMEOUT=2

echo "[Watchdog] Starting MoE Expert Node ping monitor..."

while true; do
    for ip in "${NODE_IPS[@]}"; do
        if ping -c 1 -W $TIMEOUT $ip &> /dev/null; then
            # Node is alive
            :
        else
            echo "[Watchdog] CRITICAL: Node $ip is OFFLINE!"
            # Alert the Go registry to mark experts on this node as DEAD
            curl -s -X POST "$GATEWAY_URL/mark-dead" -H "Content-Type: application/json" -d "{\"ip\": \"$ip\"}" || true
        fi
    done
    sleep 5
done
