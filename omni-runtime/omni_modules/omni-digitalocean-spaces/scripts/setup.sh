#!/bin/bash
# omni-digitalocean-spaces - Setup Script
set -e
echo 'Setting up omni-digitalocean-spaces...'
omni get omni-digitalocean-spaces
omni build
echo 'omni-digitalocean-spaces ready.'