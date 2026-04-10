#!/bin/bash
# omni-date-fns - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-date-fns healthy'