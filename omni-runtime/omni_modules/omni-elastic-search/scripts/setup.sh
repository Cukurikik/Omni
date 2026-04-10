#!/bin/bash
# omni-elastic-search - Setup Script
set -e
echo 'Setting up omni-elastic-search...'
omni get omni-elastic-search
omni build
echo 'omni-elastic-search ready.'