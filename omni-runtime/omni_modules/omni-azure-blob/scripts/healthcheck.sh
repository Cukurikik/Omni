#!/bin/bash
# omni-azure-blob - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-azure-blob healthy'