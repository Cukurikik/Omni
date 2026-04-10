#!/bin/bash
# omni-axios-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-axios-native healthy'