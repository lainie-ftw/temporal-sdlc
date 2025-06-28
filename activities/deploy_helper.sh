#!/bin/bash

# Check if environment_name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <environment_name>"
  exit 1
fi

environment_name=$1

# Source the .env file to load environment variables
if [ -f "../.env" ]; then
  export $(grep -v '^#' ../.env | xargs)
else
  echo ".env file not found"
  exit 1
fi

# Use environment variables for SSH_LOGIN and SSH_SUDO_PW
$SSH_LOGIN
cd fancy-app
git pull
chmod +x deploy.sh
export HISTIGNORE='*sudo -S*'
echo "$SSH_SUDO_PW" | sudo -S ./deploy.sh "$environment_name"
