#!/bin/bash
# omni-couchbase - Setup Script
set -e
echo 'Setting up omni-couchbase...'
omni get omni-couchbase
omni build
echo 'omni-couchbase ready.'