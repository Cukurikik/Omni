#!/bin/bash
# omni-rive-animation - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-rive-animation healthy'