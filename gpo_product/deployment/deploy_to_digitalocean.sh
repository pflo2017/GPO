#!/bin/bash

# GPO Deployment Script for DigitalOcean
# This script deploys the full GPO application to DigitalOcean

set -e  # Exit on any error

echo "🚀 GPO Deployment to DigitalOcean"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DROPLET_NAME="gpo-production"
DROPLET_SIZE="s-2vcpu-4gb"  # 2 CPU, 4GB RAM
DROPLET_REGION="nyc1"
DROPLET_IMAGE="ubuntu-22-04-x64"
DOMAIN_NAME="your-domain.com"  # Replace with your actual domain

# Environment variables (you provided these)
ENV_VARS="
# Database Configuration
SUPABASE_URL=https://dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PASSWORD=UCOXZibz5OLgTofg
SUPABASE_HOST=aws-0-eu-central-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=dbbpghthgnwozewmlzes

# Application Configuration
SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRiYnBnaHRoZ253b3pld21semVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDkzMzg5NCwiZXhwIjoyMDY2NTA5ODk0fQ.8EkU0AD3jTmBVPhdvAj_cVagLE15rV-vML5Ow0mqWuE
FLASK_ENV=production

# AI Configuration
LLM_API_KEY=AIzaSyDvFgJDn3oipZHJFcs5EBD7nU8yjwir_g
"

echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl CLI is not installed. Please install it first:${NC}"
    echo "Visit: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if authenticated
if ! doctl account get &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with DigitalOcean. Please run:${NC}"
    echo "doctl auth init"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

echo -e "${BLUE}Step 2: Creating DigitalOcean Droplet...${NC}"

# Create the droplet
echo "Creating droplet: $DROPLET_NAME"
DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
    --size $DROPLET_SIZE \
    --region $DROPLET_REGION \
    --image $DROPLET_IMAGE \
    --wait \
    --format ID,Name,Status \
    --no-header | awk '{print $1}')

echo -e "${GREEN}✅ Droplet created with ID: $DROPLET_ID${NC}"

# Wait for droplet to be ready
echo "Waiting for droplet to be ready..."
sleep 30

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
echo -e "${GREEN}✅ Droplet IP: $DROPLET_IP${NC}"

echo -e "${BLUE}Step 3: Setting up SSH access...${NC}"

# Wait for SSH to be available
echo "Waiting for SSH to be available..."
until ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$DROPLET_IP exit 2>/dev/null; do
    echo "SSH not ready yet, waiting..."
    sleep 10
done

echo -e "${GREEN}✅ SSH access confirmed${NC}"

echo -e "${BLUE}Step 4: Installing dependencies on server...${NC}"

# Install system dependencies
ssh root@$DROPLET_IP << 'EOF'
    # Update system
    apt update && apt upgrade -y
    
    # Install required packages
    apt install -y curl wget git python3 python3-pip python3-venv nginx certbot python3-certbot-nginx docker.io docker-compose
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Add user for application
    useradd -m -s /bin/bash gpo
    usermod -aG docker gpo
    
    # Create application directory
    mkdir -p /opt/gpo
    chown gpo:gpo /opt/gpo
EOF

echo -e "${GREEN}✅ Dependencies installed${NC}"

echo -e "${BLUE}Step 5: Uploading application files...${NC}"

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
cp -r gpo_product/* $TEMP_DIR/

# Create .env file
cat > $TEMP_DIR/.env << EOF
$ENV_VARS
EOF

# Upload files to server
scp -r $TEMP_DIR/* root@$DROPLET_IP:/opt/gpo/
ssh root@$DROPLET_IP "chown -R gpo:gpo /opt/gpo"

echo -e "${GREEN}✅ Application files uploaded${NC}"

echo -e "${BLUE}Step 6: Building and running Docker container...${NC}"

# Build and run the application
ssh root@$DROPLET_IP << 'EOF'
    cd /opt/gpo
    
    # Build Docker image
    docker build -t gpo-app .
    
    # Stop any existing container
    docker stop gpo-app 2>/dev/null || true
    docker rm gpo-app 2>/dev/null || true
    
    # Run the container
    docker run -d \
        --name gpo-app \
        --restart unless-stopped \
        -p 127.0.0.1:5000:5000 \
        --env-file .env \
        gpo-app
    
    # Wait for application to start
    sleep 10
    
    # Check if application is running
    if curl -f http://localhost:5000/ > /dev/null 2>&1; then
        echo "✅ Application is running"
    else
        echo "❌ Application failed to start"
        docker logs gpo-app
        exit 1
    fi
EOF

echo -e "${GREEN}✅ Docker container running${NC}"

echo -e "${BLUE}Step 7: Setting up Nginx reverse proxy...${NC}"

# Configure Nginx
ssh root@$DROPLET_IP << EOF
    cat > /etc/nginx/sites-available/gpo << 'NGINX_CONFIG'
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
NGINX_CONFIG

    # Enable the site
    ln -sf /etc/nginx/sites-available/gpo /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t
    systemctl reload nginx
    systemctl enable nginx
EOF

echo -e "${GREEN}✅ Nginx configured${NC}"

echo -e "${BLUE}Step 8: Setting up SSL certificate (if domain is configured)...${NC}"

if [ "$DOMAIN_NAME" != "your-domain.com" ]; then
    ssh root@$DROPLET_IP << EOF
        certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
EOF
    echo -e "${GREEN}✅ SSL certificate configured${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping SSL setup - please configure your domain and run:${NC}"
    echo "ssh root@$DROPLET_IP 'certbot --nginx -d your-domain.com'"
fi

echo -e "${BLUE}Step 9: Setting up monitoring and logging...${NC}"

# Create log rotation
ssh root@$DROPLET_IP << 'EOF'
    cat > /etc/logrotate.d/gpo << 'LOGROTATE_CONFIG'
/opt/gpo/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 gpo gpo
    postrotate
        docker restart gpo-app
    endscript
}
LOGROTATE_CONFIG

    # Create logs directory
    mkdir -p /opt/gpo/logs
    chown gpo:gpo /opt/gpo/logs
EOF

echo -e "${GREEN}✅ Monitoring configured${NC}"

echo -e "${BLUE}Step 10: Final verification...${NC}"

# Test the application
if curl -f http://$DROPLET_IP/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Application is accessible at http://$DROPLET_IP${NC}"
else
    echo -e "${RED}❌ Application is not accessible${NC}"
fi

# Clean up
rm -rf $TEMP_DIR

echo ""
echo -e "${GREEN}🎉 GPO Deployment Complete!${NC}"
echo "=================================="
echo -e "${BLUE}Application URL:${NC} http://$DROPLET_IP"
echo -e "${BLUE}Droplet IP:${NC} $DROPLET_IP"
echo -e "${BLUE}SSH Access:${NC} ssh root@$DROPLET_IP"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure your domain DNS to point to $DROPLET_IP"
echo "2. Run SSL setup: ssh root@$DROPLET_IP 'certbot --nginx -d your-domain.com'"
echo "3. Test the application at http://$DROPLET_IP"
echo "4. Access the dashboard at http://$DROPLET_IP/dashboard"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "View logs: ssh root@$DROPLET_IP 'docker logs gpo-app'"
echo "Restart app: ssh root@$DROPLET_IP 'docker restart gpo-app'"
echo "Update app: ssh root@$DROPLET_IP 'cd /opt/gpo && git pull && docker build -t gpo-app . && docker restart gpo-app'" 