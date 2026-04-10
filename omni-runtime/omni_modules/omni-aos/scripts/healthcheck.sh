#!/bin/bash
# omni-aos - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-aos healthy'