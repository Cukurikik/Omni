#!/bin/bash
# omni-heroku-dynos - Health Check
curl -sf http://localhost:8080/health || exit 1
echo 'omni-heroku-dynos healthy'