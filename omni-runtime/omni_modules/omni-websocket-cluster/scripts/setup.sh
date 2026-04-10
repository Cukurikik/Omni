#!/bin/bash
# omni-websocket-cluster - Setup Script
set -e
echo 'Setting up omni-websocket-cluster...'
omni get omni-websocket-cluster
omni build
echo 'omni-websocket-cluster ready.'