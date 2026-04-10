#!/bin/bash
# omni-influxdb - Setup Script
set -e
echo 'Setting up omni-influxdb...'
omni get omni-influxdb
omni build
echo 'omni-influxdb ready.'