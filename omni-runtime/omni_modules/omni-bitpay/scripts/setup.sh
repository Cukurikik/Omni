#!/bin/bash
# omni-bitpay - Setup Script
set -e
echo 'Setting up omni-bitpay...'
omni get omni-bitpay
omni build
echo 'omni-bitpay ready.'