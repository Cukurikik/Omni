#!/bin/bash
# omni-neo4j - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-neo4j healthy'