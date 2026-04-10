#!/bin/bash
# omni-neo4j - Setup Script
set -e
echo 'Setting up omni-neo4j...'
omni get omni-neo4j
omni build
echo 'omni-neo4j ready.'