#!/bin/bash
# omni-rabbitmq - Setup Script
set -e
echo 'Setting up omni-rabbitmq...'
omni get omni-rabbitmq
omni build
echo 'omni-rabbitmq ready.'