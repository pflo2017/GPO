#!/bin/bash

# Replace with your droplet IP
DROPLET_IP="134.209.236.65"

echo "Connecting to DigitalOcean droplet at $DROPLET_IP..."
ssh root@$DROPLET_IP
