#!/bin/bash
# omni-zod-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-zod-native healthy'