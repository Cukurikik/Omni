#!/bin/bash
# omni-razorpay - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-razorpay healthy'