#!/bin/bash
# omni-aws-s3 - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-aws-s3 healthy'