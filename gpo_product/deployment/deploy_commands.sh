#!/bin/bash

# Commands to run on the DigitalOcean droplet
# Replace YOUR_DROPLET_IP with your actual droplet IP

# Create application directory
mkdir -p /opt/gpo

# Copy the environment file
cp .env /opt/gpo/

# Change to application directory
cd /opt/gpo

# Clone or copy your application files
# If using git:
# git clone https://github.com/yourusername/gpo_product.git .
# Or manually copy files from your local machine

# Build Docker image
docker build -t gpo-app .

# Run the container
docker run -d \
  --name gpo-app \
  --restart unless-stopped \
  -p 80:5000 \
  --env-file .env \
  gpo-app

# Install and configure Nginx
apt update && apt install -y nginx

# Create Nginx configuration
cat > /etc/nginx/sites-available/gpo << 'NGINX_CONFIG'
server {
    listen 80;
    server_name YOUR_DROPLET_IP;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_CONFIG

# Enable the site and reload Nginx
ln -sf /etc/nginx/sites-available/gpo /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "Deployment complete! Your application should be accessible at http://YOUR_DROPLET_IP"
