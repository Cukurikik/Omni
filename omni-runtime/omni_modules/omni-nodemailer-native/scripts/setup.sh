#!/bin/bash
# omni-nodemailer-native - Setup Script
set -e
echo 'Setting up omni-nodemailer-native...'
omni get omni-nodemailer-native
omni build
echo 'omni-nodemailer-native ready.'