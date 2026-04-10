#!/bin/bash
# omni-influxdb - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-influxdb healthy'