#!/bin/bash
# omni-canvas-turbo - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-canvas-turbo healthy'