#!/bin/bash
# omni-wasabi-s3 - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-wasabi-s3 healthy'