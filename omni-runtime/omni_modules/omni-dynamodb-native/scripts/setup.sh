#!/bin/bash
# omni-dynamodb-native - Setup Script
set -e
echo 'Setting up omni-dynamodb-native...'
omni get omni-dynamodb-native
omni build
echo 'omni-dynamodb-native ready.'