#!/bin/bash
# omni-timescaledb - Setup Script
set -e
echo 'Setting up omni-timescaledb...'
omni get omni-timescaledb
omni build
echo 'omni-timescaledb ready.'