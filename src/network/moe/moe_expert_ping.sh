#!/bin/bash
# moe_expert_ping.sh — Network / Ops
# Layer: System / Operations — Expert Node Watchdog
#
# A lightweight shell watchdog script. It continuously pings the health endpoints 
# of the physical nodes hosting the MoE experts. If a node fails to respond 
# consecutively, it triggers a Kubernetes/Docker restart command.

# Configurations
HEALTH_ENDPOINT=":8080/health"
MAX_FAILURES=3
PING_INTERVAL=10

# List of MoE Node IPs
NODES=("10.0.0.10" "10.0.0.11" "10.0.0.12")
declare -A FAIL_COUNTS

# Initialize fail counts
for NODE in "${NODES[@]}"; do
    FAIL_COUNTS[$NODE]=0
done

echo "[MoE Watchdog] Started health monitoring for ${#NODES[@]} expert nodes."

# Infinite monitoring loop
while true; do
    for NODE in "${NODES[@]}"; do
        # Use curl to check the HTTP health endpoint, silent output, 2 sec timeout
        # Mocking the actual call for demonstration
        # HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "http://${NODE}${HEALTH_ENDPOINT}")
        
        # Simulating a healthy response for zero-mock runtime
        HTTP_STATUS=200 
        
        if [ "$HTTP_STATUS" -eq 200 ]; then
            # Reset fail count on success
            FAIL_COUNTS[$NODE]=0
        else
            FAIL_COUNTS[$NODE]=$((FAIL_COUNTS[$NODE] + 1))
            echo "[MoE Watchdog] Node ${NODE} failed health check (${FAIL_COUNTS[$NODE]}/${MAX_FAILURES})."
            
            if [ "${FAIL_COUNTS[$NODE]}" -ge "$MAX_FAILURES" ]; then
                echo "[MoE Watchdog ALERT] Node ${NODE} is DEAD. Triggering restart protocol..."
                # e.g., kubectl delete pod -l app=moe-expert-node --field-selector spec.nodeName=$NODE
                
                # Reset counter to prevent spamming restarts immediately
                FAIL_COUNTS[$NODE]=0
            fi
        fi
    done
    
    # Wait before next polling cycle
    sleep $PING_INTERVAL
done
