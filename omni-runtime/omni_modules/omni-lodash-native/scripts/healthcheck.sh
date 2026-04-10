#!/bin/bash
# omni-lodash-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-lodash-native healthy'