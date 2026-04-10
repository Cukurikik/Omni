#!/bin/bash
# omni-braintree - Setup Script
set -e
echo 'Setting up omni-braintree...'
omni get omni-braintree
omni build
echo 'omni-braintree ready.'