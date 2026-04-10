#!/bin/bash
# omni-bcrypt-native - Setup Script
set -e
echo 'Setting up omni-bcrypt-native...'
omni get omni-bcrypt-native
omni build
echo 'omni-bcrypt-native ready.'