#!/bin/bash
# omni-date-fns - Setup Script
set -e
echo 'Setting up omni-date-fns...'
omni get omni-date-fns
omni build
echo 'omni-date-fns ready.'