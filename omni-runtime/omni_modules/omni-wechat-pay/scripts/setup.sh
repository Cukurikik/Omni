#!/bin/bash
# omni-wechat-pay - Setup Script
set -e
echo 'Setting up omni-wechat-pay...'
omni get omni-wechat-pay
omni build
echo 'omni-wechat-pay ready.'