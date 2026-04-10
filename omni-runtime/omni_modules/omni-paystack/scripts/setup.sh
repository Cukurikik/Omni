#!/bin/bash
# omni-paystack - Setup Script
set -e
echo 'Setting up omni-paystack...'
omni get omni-paystack
omni build
echo 'omni-paystack ready.'