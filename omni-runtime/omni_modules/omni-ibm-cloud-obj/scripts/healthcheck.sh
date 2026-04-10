#!/bin/bash
# omni-ibm-cloud-obj - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-ibm-cloud-obj healthy'