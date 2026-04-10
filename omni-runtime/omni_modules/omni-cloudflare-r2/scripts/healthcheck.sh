#!/bin/bash
# omni-cloudflare-r2 - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-cloudflare-r2 healthy'