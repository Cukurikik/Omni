#!/bin/bash
# omni-supabase-storage - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-supabase-storage healthy'