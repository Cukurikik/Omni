#!/bin/bash
# omni-paypal - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-paypal healthy'