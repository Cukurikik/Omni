#!/bin/bash
# omni-eslint-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-eslint-native healthy'