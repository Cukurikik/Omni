#!/bin/bash
# omni-bitpay - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-bitpay healthy'