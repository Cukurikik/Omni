#!/bin/bash
# omni-tencent-cos - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-tencent-cos healthy'