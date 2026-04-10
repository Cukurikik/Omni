#!/bin/bash
# omni-anime-js - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-anime-js healthy'