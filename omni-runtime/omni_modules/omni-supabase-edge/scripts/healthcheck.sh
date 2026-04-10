#!/bin/bash
# omni-supabase-edge - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-supabase-edge healthy'