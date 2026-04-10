#!/bin/bash
# omni-scaleway-obj - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-scaleway-obj healthy'