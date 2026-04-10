#!/bin/bash
# omni-zod-native - Setup Script
set -e
echo 'Setting up omni-zod-native...'
omni get omni-zod-native
omni build
echo 'omni-zod-native ready.'