#!/bin/bash
# omni-wechat-pay - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-wechat-pay healthy'