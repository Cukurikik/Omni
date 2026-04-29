#!/usr/bin/env bash
# OMNI Environment Verification Script

echo "Checking OMNI Developer Environment..."
omni --version || { echo "OMNI CLI not installed! Install via curl https://nexus.omniframework.dev/install.sh"; exit 1; }

echo "Running complete system audit..."
omni check --strict

echo "Generating universal binaries..."
omni build --release --target all

echo "Deploying to Nexus..."
omni publish

echo "Process completed successfully."
