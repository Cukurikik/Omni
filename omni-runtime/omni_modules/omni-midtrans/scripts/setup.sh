#!/bin/bash
# omni-midtrans - Setup Script
set -e
echo 'Setting up omni-midtrans...'
omni get omni-midtrans
omni build
echo 'omni-midtrans ready.'