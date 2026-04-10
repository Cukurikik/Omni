#!/bin/bash
# omni-digitalocean-spaces - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-digitalocean-spaces healthy'