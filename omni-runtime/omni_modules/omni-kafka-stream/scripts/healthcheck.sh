#!/bin/bash
# omni-kafka-stream - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-kafka-stream healthy'