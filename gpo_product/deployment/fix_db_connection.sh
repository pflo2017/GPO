#!/bin/bash

# Replace with your droplet IP
DROPLET_IP="134.209.236.65"

echo "Updating environment variables on $DROPLET_IP..."

# Create the updated .env file with the correct Supabase host
cat > temp_env << 'EOF'
# Database Configuration
SUPABASE_URL=https://dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PASSWORD=UCOXZibz5OLgTofg
SUPABASE_HOST=db.dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=postgres

# Application Configuration
SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRiYnBnaHRoZ253b3pld21semVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDkzMzg5NCwiZXhwIjoyMDY2NTA5ODk0fQ.8EkU0AD3jTmBVPhdvAj_cVagLE15rV-vML5Ow0mqWuE
FLASK_ENV=production

# AI Configuration
LLM_API_KEY=AIzaSyDvFgJDn3oipZHJFcs5EBD7nU8yjwir_gU
EOF

# Upload the file to the server
scp temp_env root@$DROPLET_IP:/opt/gpo/.env

# Copy it into the Docker container
ssh root@$DROPLET_IP "docker cp /opt/gpo/.env gpo-app:/app/.env"

# Restart the container
ssh root@$DROPLET_IP "docker restart gpo-app"

# Clean up
rm temp_env

echo "Environment variables updated and container restarted!"
echo "Waiting for the application to start..."
sleep 5

# Check if the database connection is working
echo "Checking database connection..."
ssh root@$DROPLET_IP "docker exec gpo-app bash -c 'curl -s http://localhost:5000/dashboard | grep -i error'"

echo "Done! Your application should now be fully functional."
echo "Access it at: http://$DROPLET_IP/" 