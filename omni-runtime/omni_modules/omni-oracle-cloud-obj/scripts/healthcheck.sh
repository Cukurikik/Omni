#!/bin/bash
# omni-oracle-cloud-obj - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-oracle-cloud-obj healthy'