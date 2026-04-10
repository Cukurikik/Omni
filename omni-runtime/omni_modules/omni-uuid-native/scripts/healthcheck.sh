#!/bin/bash
# omni-uuid-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-uuid-native healthy'