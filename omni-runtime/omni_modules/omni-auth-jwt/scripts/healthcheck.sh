#!/bin/bash
# omni-auth-jwt - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-auth-jwt healthy'