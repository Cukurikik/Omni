#!/bin/bash
# omni-netlify-edge - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-netlify-edge healthy'