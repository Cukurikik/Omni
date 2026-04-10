#!/bin/bash
# omni-xendit - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-xendit healthy'