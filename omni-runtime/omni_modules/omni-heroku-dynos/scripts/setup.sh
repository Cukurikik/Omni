#!/bin/bash
# omni-heroku-dynos - Setup Script
set -e
echo 'Setting up omni-heroku-dynos...'
omni get omni-heroku-dynos
omni build
echo 'omni-heroku-dynos ready.'