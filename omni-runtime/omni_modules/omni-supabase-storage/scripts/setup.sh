#!/bin/bash
# omni-supabase-storage - Setup Script
set -e
echo 'Setting up omni-supabase-storage...'
omni get omni-supabase-storage
omni build
echo 'omni-supabase-storage ready.'