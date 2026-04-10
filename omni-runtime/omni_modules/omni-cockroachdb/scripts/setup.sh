#!/bin/bash
# omni-cockroachdb - Setup Script
set -e
echo 'Setting up omni-cockroachdb...'
omni get omni-cockroachdb
omni build
echo 'omni-cockroachdb ready.'