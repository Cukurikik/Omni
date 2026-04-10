#!/bin/bash
# omni-postgresql - Setup Script
set -e
echo 'Setting up omni-postgresql...'
omni get omni-postgresql
omni build
echo 'omni-postgresql ready.'