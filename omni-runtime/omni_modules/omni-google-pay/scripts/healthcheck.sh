#!/bin/bash
# omni-google-pay - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-google-pay healthy'