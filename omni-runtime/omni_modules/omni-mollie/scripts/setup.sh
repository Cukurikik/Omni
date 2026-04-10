#!/bin/bash
# omni-mollie - Setup Script
set -e
echo 'Setting up omni-mollie...'
omni get omni-mollie
omni build
echo 'omni-mollie ready.'