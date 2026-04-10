#!/bin/bash
# omni-dynamodb-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-dynamodb-native healthy'