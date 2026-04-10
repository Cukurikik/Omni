#!/bin/bash
# omni-socket-io-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-socket-io-native healthy'