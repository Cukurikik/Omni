#!/bin/bash
# omni-gsap - Setup Script
set -e
echo 'Setting up omni-gsap...'
omni get omni-gsap
omni build
echo 'omni-gsap ready.'