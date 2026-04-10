#!/bin/bash
# omni-graphql-federation - Setup Script
set -e
echo 'Setting up omni-graphql-federation...'
omni get omni-graphql-federation
omni build
echo 'omni-graphql-federation ready.'