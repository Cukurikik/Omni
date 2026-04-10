#!/bin/bash
# omni-coinbase-commerce - Setup Script
set -e
echo 'Setting up omni-coinbase-commerce...'
omni get omni-coinbase-commerce
omni build
echo 'omni-coinbase-commerce ready.'