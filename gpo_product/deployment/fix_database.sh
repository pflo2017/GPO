#!/bin/bash

# Replace with your droplet IP
DROPLET_IP="134.209.236.65"

echo "Uploading database initialization script to $DROPLET_IP..."
scp $(dirname "$0")/init_db.py root@$DROPLET_IP:/opt/gpo/

echo "Running database initialization script on $DROPLET_IP..."
ssh root@$DROPLET_IP "cd /opt/gpo && python3 init_db.py"

echo "Restarting the application container..."
ssh root@$DROPLET_IP "docker restart gpo-app"

echo "Done! Your application should now be fully functional."
echo "Access it at: http://$DROPLET_IP/" 