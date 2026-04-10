#!/bin/bash
# omni-sqlite-turbo - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-sqlite-turbo healthy'