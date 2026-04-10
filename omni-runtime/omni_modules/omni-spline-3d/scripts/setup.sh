#!/bin/bash
# omni-spline-3d - Setup Script
set -e
echo 'Setting up omni-spline-3d...'
omni get omni-spline-3d
omni build
echo 'omni-spline-3d ready.'