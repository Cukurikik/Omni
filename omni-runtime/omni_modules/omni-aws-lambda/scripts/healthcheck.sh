#!/bin/bash
# omni-aws-lambda - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-aws-lambda healthy'