#!/bin/bash

# Replace with your droplet IP
DROPLET_IP="134.209.236.65"

echo "Checking deployment status on $DROPLET_IP..."

# Check if Docker is running
echo "Docker status:"
ssh root@$DROPLET_IP "systemctl status docker | grep Active"

# Check if our container is running
echo -e "\nContainer status:"
ssh root@$DROPLET_IP "docker ps | grep gpo-app"

# Check if the application is responding
echo -e "\nApplication response:"
ssh root@$DROPLET_IP "curl -s http://localhost:80/ | head -n 10"

echo -e "\nDeployment check complete!"
