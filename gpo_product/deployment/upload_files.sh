#!/bin/bash

# Replace with your droplet IP
DROPLET_IP="134.209.236.65"

# Create remote directory
ssh root@$DROPLET_IP "mkdir -p /opt/gpo"

# Upload environment file
scp .env root@$DROPLET_IP:/opt/gpo/

# Upload application files
scp -r ../gpo_product/* root@$DROPLET_IP:/opt/gpo/

echo "Files uploaded successfully to $DROPLET_IP"
