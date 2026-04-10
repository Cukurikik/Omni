#!/bin/bash
# omni-parallax-core - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-parallax-core healthy'