#!/bin/bash
# omni-kafka-stream - Setup Script
set -e
echo 'Setting up omni-kafka-stream...'
omni get omni-kafka-stream
omni build
echo 'omni-kafka-stream ready.'