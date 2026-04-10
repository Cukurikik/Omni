#!/bin/bash
# omni-mollie - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-mollie healthy'