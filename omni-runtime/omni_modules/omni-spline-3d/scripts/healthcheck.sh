#!/bin/bash
# omni-spline-3d - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-spline-3d healthy'