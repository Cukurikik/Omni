#!/bin/bash
# omni-authorize-net - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-authorize-net healthy'