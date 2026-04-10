#!/bin/bash
# omni-faunadb - Setup Script
set -e
echo 'Setting up omni-faunadb...'
omni get omni-faunadb
omni build
echo 'omni-faunadb ready.'