#!/bin/bash
# omni-klarna - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-klarna healthy'