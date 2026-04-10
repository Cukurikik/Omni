#!/bin/bash
# omni-parallax-core - Setup Script
set -e
echo 'Setting up omni-parallax-core...'
omni get omni-parallax-core
omni build
echo 'omni-parallax-core ready.'