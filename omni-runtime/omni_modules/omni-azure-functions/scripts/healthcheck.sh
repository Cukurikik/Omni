#!/bin/bash
# omni-azure-functions - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-azure-functions healthy'