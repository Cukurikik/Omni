#!/bin/bash
# omni-auth-jwt - Setup Script
set -e
echo 'Setting up omni-auth-jwt...'
omni get omni-auth-jwt
omni build
echo 'omni-auth-jwt ready.'