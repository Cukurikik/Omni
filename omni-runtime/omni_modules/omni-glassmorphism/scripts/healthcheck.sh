#!/bin/bash
# omni-glassmorphism - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-glassmorphism healthy'