#!/bin/bash
# omni-framer-motion - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-framer-motion healthy'