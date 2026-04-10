#!/bin/bash
# omni-prettier-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-prettier-native healthy'