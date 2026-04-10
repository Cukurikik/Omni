#!/bin/bash
# omni-image-optimizer - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-image-optimizer healthy'