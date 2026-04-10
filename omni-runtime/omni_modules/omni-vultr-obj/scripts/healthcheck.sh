#!/bin/bash
# omni-vultr-obj - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-vultr-obj healthy'