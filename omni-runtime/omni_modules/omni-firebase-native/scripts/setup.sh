#!/bin/bash
# omni-firebase-native - Setup Script
set -e
echo 'Setting up omni-firebase-native...'
omni get omni-firebase-native
omni build
echo 'omni-firebase-native ready.'