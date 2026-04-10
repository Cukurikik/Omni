#!/bin/bash
# omni-mariadb - Setup Script
set -e
echo 'Setting up omni-mariadb...'
omni get omni-mariadb
omni build
echo 'omni-mariadb ready.'