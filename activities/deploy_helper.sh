#!/bin/bash

# Initialize variables
ENV_NAME=""
SSH_PW=""
SSH_USER=""
SSH_IP=""

# Parse command line options
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --env_name) ENV_NAME="$2"; shift ;;
    --ssh_pw) SSH_PW="$2"; shift ;;
    --ssh_user) SSH_USER="$2"; shift ;;
    --ssh_ip) SSH_IP="$2"; shift ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Check if all required parameters are provided
if [ -z "$ENV_NAME" ] || [ -z "$SSH_PW" ] || [ -z "$SSH_USER" ] || [ -z "$SSH_IP" ]; then
  echo "Usage: $0 --env_name <ENV_NAME> --ssh_pw <SSH_PW> --ssh_user <SSH_USER> --ssh_ip <SSH_IP>"
  exit 1
fi

# Use provided parameters for SSH details
sshpass -p "$SSH_PW" ssh $SSH_USER@$SSH_IP
cd fancy-app
git pull
chmod +x deploy.sh
export HISTIGNORE='*sudo -S*'
echo "$SSH_PW" | sudo -S ./deploy.sh "$ENV_NAME"
