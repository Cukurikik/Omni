#!/bin/bash
# omni-moment-turbo - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-moment-turbo healthy'