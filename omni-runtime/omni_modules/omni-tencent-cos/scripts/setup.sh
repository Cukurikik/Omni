#!/bin/bash
# omni-tencent-cos - Setup Script
set -e
echo 'Setting up omni-tencent-cos...'
omni get omni-tencent-cos
omni build
echo 'omni-tencent-cos ready.'