#!/bin/bash
# omni-ibm-cloud-obj - Setup Script
set -e
echo 'Setting up omni-ibm-cloud-obj...'
omni get omni-ibm-cloud-obj
omni build
echo 'omni-ibm-cloud-obj ready.'