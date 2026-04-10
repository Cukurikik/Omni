#!/bin/bash
# omni-nodemailer-native - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-nodemailer-native healthy'