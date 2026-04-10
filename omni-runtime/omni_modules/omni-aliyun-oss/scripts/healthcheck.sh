#!/bin/bash
# omni-aliyun-oss - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-aliyun-oss healthy'