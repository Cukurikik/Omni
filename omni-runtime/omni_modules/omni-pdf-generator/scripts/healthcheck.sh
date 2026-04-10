#!/bin/bash
# omni-pdf-generator - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-pdf-generator healthy'