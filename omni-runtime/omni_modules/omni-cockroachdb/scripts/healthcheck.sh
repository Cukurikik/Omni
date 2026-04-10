#!/bin/bash
# omni-cockroachdb - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-cockroachdb healthy'