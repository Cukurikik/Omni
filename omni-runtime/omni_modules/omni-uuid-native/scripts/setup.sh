#!/bin/bash
# omni-uuid-native - Setup Script
set -e
echo 'Setting up omni-uuid-native...'
omni get omni-uuid-native
omni build
echo 'omni-uuid-native ready.'