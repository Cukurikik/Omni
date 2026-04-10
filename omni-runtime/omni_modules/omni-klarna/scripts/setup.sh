#!/bin/bash
# omni-klarna - Setup Script
set -e
echo 'Setting up omni-klarna...'
omni get omni-klarna
omni build
echo 'omni-klarna ready.'