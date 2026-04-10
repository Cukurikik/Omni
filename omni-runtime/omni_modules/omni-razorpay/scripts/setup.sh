#!/bin/bash
# omni-razorpay - Setup Script
set -e
echo 'Setting up omni-razorpay...'
omni get omni-razorpay
omni build
echo 'omni-razorpay ready.'