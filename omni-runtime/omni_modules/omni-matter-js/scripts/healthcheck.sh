#!/bin/bash
# omni-matter-js - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-matter-js healthy'