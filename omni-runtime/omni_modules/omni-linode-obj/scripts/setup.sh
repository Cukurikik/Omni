#!/bin/bash
# omni-linode-obj - Setup Script
set -e
echo 'Setting up omni-linode-obj...'
omni get omni-linode-obj
omni build
echo 'omni-linode-obj ready.'