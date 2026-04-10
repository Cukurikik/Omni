#!/bin/bash
# omni-milvus - Setup Script
set -e
echo 'Setting up omni-milvus...'
omni get omni-milvus
omni build
echo 'omni-milvus ready.'