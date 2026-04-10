#!/bin/bash
# omni-afterpay - Setup Script
set -e
echo 'Setting up omni-afterpay...'
omni get omni-afterpay
omni build
echo 'omni-afterpay ready.'