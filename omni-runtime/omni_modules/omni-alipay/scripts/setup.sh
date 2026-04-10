#!/bin/bash
# omni-alipay - Setup Script
set -e
echo 'Setting up omni-alipay...'
omni get omni-alipay
omni build
echo 'omni-alipay ready.'