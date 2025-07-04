#!/bin/bash

# Replace with your droplet IP
DROPLET_IP="134.209.236.65"

echo "Creating a script to fix the app.py file on $DROPLET_IP..."

# Create a script to modify the app.py file
cat > fix_app_py_remote.sh << 'EOF'
#!/bin/bash

# Extract the app.py file from the container
docker cp gpo-app:/app/app.py /tmp/app.py

# Create a backup
cp /tmp/app.py /tmp/app.py.bak

# Modify the file to use the correct database connection
sed -i 's/aws-0-eu-central-1.pooler.supabase.com/db.dbbpghthgnwozewmlzes.supabase.co/g' /tmp/app.py

# Add a direct connection string that doesn't rely on environment variables
sed -i 's/app.config\[\x27SQLALCHEMY_DATABASE_URI\x27\] = f"postgresql:\/\/postgres:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}\/{SUPABASE_DB}"/app.config\[\x27SQLALCHEMY_DATABASE_URI\x27\] = "postgresql:\/\/postgres:UCOXZibz5OLgTofg@db.dbbpghthgnwozewmlzes.supabase.co:6543\/postgres"/g' /tmp/app.py

# Copy the modified file back to the container
docker cp /tmp/app.py gpo-app:/app/app.py

# Restart the container
docker restart gpo-app

echo "app.py file updated and container restarted!"
EOF

# Upload the script to the server
scp fix_app_py_remote.sh root@$DROPLET_IP:/opt/gpo/

# Make the script executable and run it
ssh root@$DROPLET_IP "chmod +x /opt/gpo/fix_app_py_remote.sh && /opt/gpo/fix_app_py_remote.sh"

# Clean up
rm fix_app_py_remote.sh

echo "Done! Your application should now be fully functional."
echo "Access it at: http://$DROPLET_IP/" 