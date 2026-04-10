#!/bin/bash
# omni-oracle-cloud-obj - Setup Script
set -e
echo 'Setting up omni-oracle-cloud-obj...'
omni get omni-oracle-cloud-obj
omni build
echo 'omni-oracle-cloud-obj ready.'