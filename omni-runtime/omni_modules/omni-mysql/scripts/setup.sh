#!/bin/bash
# omni-mysql - Setup Script
set -e
echo 'Setting up omni-mysql...'
omni get omni-mysql
omni build
echo 'omni-mysql ready.'