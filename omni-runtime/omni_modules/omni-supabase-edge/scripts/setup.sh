#!/bin/bash
# omni-supabase-edge - Setup Script
set -e
echo 'Setting up omni-supabase-edge...'
omni get omni-supabase-edge
omni build
echo 'omni-supabase-edge ready.'