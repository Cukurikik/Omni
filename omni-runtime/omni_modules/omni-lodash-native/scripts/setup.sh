#!/bin/bash
# omni-lodash-native - Setup Script
set -e
echo 'Setting up omni-lodash-native...'
omni get omni-lodash-native
omni build
echo 'omni-lodash-native ready.'