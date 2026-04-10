#!/bin/bash
# omni-cloudflare-workers - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-cloudflare-workers healthy'