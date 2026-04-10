#!/bin/bash
# omni-wow-js - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-wow-js healthy'