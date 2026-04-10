#!/bin/bash
# omni-adyen - Setup Script
set -e
echo 'Setting up omni-adyen...'
omni get omni-adyen
omni build
echo 'omni-adyen ready.'