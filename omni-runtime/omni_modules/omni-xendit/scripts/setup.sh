#!/bin/bash
# omni-xendit - Setup Script
set -e
echo 'Setting up omni-xendit...'
omni get omni-xendit
omni build
echo 'omni-xendit ready.'