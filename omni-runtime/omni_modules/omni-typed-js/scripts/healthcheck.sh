#!/bin/bash
# omni-typed-js - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-typed-js healthy'