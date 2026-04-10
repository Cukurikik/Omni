#!/bin/bash
# omni-p5-js - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-p5-js healthy'