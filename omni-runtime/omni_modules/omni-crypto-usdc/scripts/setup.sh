#!/bin/bash
# omni-crypto-usdc - Setup Script
set -e
echo 'Setting up omni-crypto-usdc...'
omni get omni-crypto-usdc
omni build
echo 'omni-crypto-usdc ready.'