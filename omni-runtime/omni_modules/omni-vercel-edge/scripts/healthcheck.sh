#!/bin/bash
# omni-vercel-edge - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-vercel-edge healthy'