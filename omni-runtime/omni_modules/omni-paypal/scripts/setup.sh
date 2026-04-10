#!/bin/bash
# omni-paypal - Setup Script
set -e
echo 'Setting up omni-paypal...'
omni get omni-paypal
omni build
echo 'omni-paypal ready.'