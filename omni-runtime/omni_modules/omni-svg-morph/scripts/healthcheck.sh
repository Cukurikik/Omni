#!/bin/bash
# omni-svg-morph - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-svg-morph healthy'