#!/bin/bash
# omni-linode-obj - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-linode-obj healthy'