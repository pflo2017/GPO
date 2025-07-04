# GPO Deployment Guide

This guide provides detailed instructions for deploying the GPO (Project Orchestrator) application in production environments.

## 📋 Prerequisites

Before deploying, ensure you have:

- **Docker** installed on your server
- **Supabase** project configured with database tables
- **Google Gemini API key** for AI functionality
- **Domain name** (optional, for production)
- **SSL certificate** (recommended for production)

## 🐳 Docker Deployment (Recommended)

### 1. Build the Docker Image

```bash
# Clone the repository
git clone <repository-url>
cd gpo_product

# Build the Docker image
docker build -t gpo-product .
```

### 2. Run the Container

```bash
# Basic run command
docker run -d \
  --name gpo-app \
  -p 5000:5000 \
  -e SUPABASE_URL='your_supabase_url' \
  -e SUPABASE_PASSWORD='your_supabase_password' \
  -e SECRET_KEY='your_secure_secret_key' \
  -e LLM_API_KEY='your_gemini_api_key' \
  -e FLASK_ENV='production' \
  gpo-product
```

### 3. Environment Variables

Create a `.env` file for easier management:

```env
# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_PASSWORD=your_database_password
SUPABASE_HOST=db.yourproject.supabase.co
SUPABASE_PORT=6543
SUPABASE_DB=postgres

# Application Configuration
SECRET_KEY=your_very_secure_random_secret_key
FLASK_ENV=production

# AI Configuration
LLM_API_KEY=your_google_gemini_api_key
```

### 4. Run with Environment File

```bash
docker run -d \
  --name gpo-app \
  -p 5000:5000 \
  --env-file .env \
  gpo-product
```

## 🌐 Production Deployment with Reverse Proxy

### Option 1: Nginx + Docker

1. **Create Nginx Configuration**

```nginx
# /etc/nginx/sites-available/gpo
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Enable the Site**

```bash
sudo ln -s /etc/nginx/sites-available/gpo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

3. **Run Docker Container**

```bash
docker run -d \
  --name gpo-app \
  --restart unless-stopped \
  -p 127.0.0.1:5000:5000 \
  --env-file .env \
  gpo-product
```

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  gpo-app:
    build: .
    container_name: gpo-app
    restart: unless-stopped
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_PASSWORD=${SUPABASE_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - LLM_API_KEY=${LLM_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
      - ./dummy_docs:/app/dummy_docs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: gpo-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - gpo-app
```

Run with:

```bash
docker-compose up -d
```

## 🔒 SSL/HTTPS Configuration

### Using Let's Encrypt with Certbot

1. **Install Certbot**

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

2. **Obtain SSL Certificate**

```bash
sudo certbot --nginx -d your-domain.com
```

3. **Auto-renewal**

```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### 1. Application Logs

```bash
# View application logs
docker logs gpo-app

# Follow logs in real-time
docker logs -f gpo-app

# View logs from the last hour
docker logs --since 1h gpo-app
```

### 2. Health Checks

The application includes built-in health checks:

```bash
# Check if the application is responding
curl -f http://localhost:5000/

# Check Docker health status
docker inspect gpo-app | grep Health -A 10
```

### 3. Resource Monitoring

```bash
# Monitor container resources
docker stats gpo-app

# Check disk usage
docker system df
```

## 🔧 Production Optimizations

### 1. Gunicorn Configuration

The application uses optimized Gunicorn settings:

- **Workers**: 4 (adjust based on CPU cores)
- **Worker Class**: sync
- **Max Requests**: 1000 per worker
- **Timeout**: 30 seconds
- **Keep-alive**: 2 seconds

### 2. Database Connection Pooling

Consider using Supabase's connection pooler for better performance:

```env
SUPABASE_HOST=db.yourproject.supabase.co:6543
```

### 3. File Storage

For production, consider using cloud storage (AWS S3, Google Cloud Storage) instead of local file storage.

## 🚨 Security Considerations

### 1. Environment Variables

- Never commit `.env` files to version control
- Use strong, randomly generated secret keys
- Rotate API keys regularly

### 2. Network Security

- Use firewalls to restrict access
- Consider using VPN for database access
- Implement rate limiting

### 3. Container Security

```bash
# Run container with non-root user
docker run --user 1000:1000 gpo-product

# Limit container resources
docker run --memory=512m --cpus=1 gpo-product
```

## 🔄 Updates and Maintenance

### 1. Application Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### 2. Database Backups

```bash
# Backup Supabase data (using Supabase dashboard or CLI)
supabase db dump --db-url "your_connection_string" > backup.sql
```

### 3. Log Rotation

```bash
# Configure log rotation in /etc/logrotate.d/gpo
/app/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check Supabase credentials
   - Verify network connectivity
   - Check database status in Supabase dashboard

2. **LLM API Errors**
   - Verify Gemini API key
   - Check API quota and limits
   - Review application logs

3. **Container Won't Start**
   - Check Docker logs: `docker logs gpo-app`
   - Verify environment variables
   - Check port availability

4. **Performance Issues**
   - Monitor resource usage: `docker stats`
   - Check database performance
   - Review Gunicorn worker configuration

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```bash
docker run -e FLASK_ENV=development gpo-product
```

## 📞 Support

For deployment issues:

1. Check the application logs
2. Review this deployment guide
3. Contact support with specific error messages
4. Include relevant logs and configuration details

---

**Next Steps**: After successful deployment, proceed to the [API Documentation](API.md) and [Demo Script](DEMO_SCRIPT.md) for sales presentations. 