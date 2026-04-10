#!/bin/bash
# omni-weaviate - Setup Script
set -e
echo 'Setting up omni-weaviate...'
omni get omni-weaviate
omni build
echo 'omni-weaviate ready.'