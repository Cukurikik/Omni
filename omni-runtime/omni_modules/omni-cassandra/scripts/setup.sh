#!/bin/bash
# omni-cassandra - Setup Script
set -e
echo 'Setting up omni-cassandra...'
omni get omni-cassandra
omni build
echo 'omni-cassandra ready.'