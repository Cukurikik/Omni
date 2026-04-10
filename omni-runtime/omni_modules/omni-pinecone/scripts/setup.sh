#!/bin/bash
# omni-pinecone - Setup Script
set -e
echo 'Setting up omni-pinecone...'
omni get omni-pinecone
omni build
echo 'omni-pinecone ready.'