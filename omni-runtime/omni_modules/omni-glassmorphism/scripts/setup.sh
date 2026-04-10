#!/bin/bash
# omni-glassmorphism - Setup Script
set -e
echo 'Setting up omni-glassmorphism...'
omni get omni-glassmorphism
omni build
echo 'omni-glassmorphism ready.'