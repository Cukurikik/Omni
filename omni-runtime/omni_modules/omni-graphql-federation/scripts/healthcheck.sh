#!/bin/bash
# omni-graphql-federation - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-graphql-federation healthy'