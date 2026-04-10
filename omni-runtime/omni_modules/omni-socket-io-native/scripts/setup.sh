#!/bin/bash
# omni-socket-io-native - Setup Script
set -e
echo 'Setting up omni-socket-io-native...'
omni get omni-socket-io-native
omni build
echo 'omni-socket-io-native ready.'