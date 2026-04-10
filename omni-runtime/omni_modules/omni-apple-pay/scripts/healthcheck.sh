#!/bin/bash
# omni-apple-pay - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-apple-pay healthy'