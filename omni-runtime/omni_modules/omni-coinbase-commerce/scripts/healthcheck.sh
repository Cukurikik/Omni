#!/bin/bash
# omni-coinbase-commerce - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-coinbase-commerce healthy'