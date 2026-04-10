#!/bin/bash
# omni-websocket-cluster - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-websocket-cluster healthy'