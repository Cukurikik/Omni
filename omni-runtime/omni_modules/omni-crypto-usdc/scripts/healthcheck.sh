#!/bin/bash
# omni-crypto-usdc - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-crypto-usdc healthy'