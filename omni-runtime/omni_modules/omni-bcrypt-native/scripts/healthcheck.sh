#!/bin/bash
# omni-bcrypt-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-bcrypt-native healthy'