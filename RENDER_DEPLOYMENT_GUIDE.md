# Render Deployment Guide for GPO

## Current Status
✅ **Local Development**: Working perfectly  
❌ **Render Deployment**: Failing with "Exited with status 1"

## Environment Variables Required

The application has default values, but for production you should set these in Render:

### Required Environment Variables
```
SUPABASE_HOST=aws-0-eu-central-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_USER=postgres.dbbpghthgnwozewmlzes
SUPABASE_PASSWORD=UCOXZibz5OLgTofg
SUPABASE_DB=postgres
SECRET_KEY=<generate-a-secure-secret-key>
FLASK_ENV=production
```

### How to Set Environment Variables in Render
1. Go to your Render dashboard
2. Select your GPO service
3. Go to "Environment" tab
4. Add each variable above

## Deployment Configuration

### Current render.yaml
```yaml
services:
  - type: web
    name: gpo-cloud-gpo
    env: python
    plan: free
    buildCommand: |
      pip install -r requirements.txt
    startCommand: |
      gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: SUPABASE_HOST
        sync: false
      - key: SUPABASE_DB
        sync: false
      - key: SUPABASE_USER
        sync: false
      - key: SUPABASE_PASSWORD
        sync: false
      - key: SUPABASE_PORT
        value: 5432
```

## Troubleshooting Steps

### 1. Check Render Logs
- Go to your service in Render dashboard
- Click on "Logs" tab
- Look for specific error messages

### 2. Common Issues and Solutions

#### Issue: Import Errors
**Solution**: The wsgi.py file handles imports correctly

#### Issue: Missing Dependencies
**Solution**: Check requirements.txt includes all needed packages

#### Issue: Database Connection
**Solution**: Ensure environment variables are set correctly

#### Issue: Port Configuration
**Solution**: Render automatically sets $PORT environment variable

### 3. Test Deployment Locally
```bash
# Test the exact deployment command
gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app
```

### 4. Verify Requirements
Make sure all dependencies are in requirements.txt:
- Flask
- SQLAlchemy
- psycopg2-binary
- python-dotenv
- gunicorn
- flask-login
- werkzeug

## Next Steps

1. **Set Environment Variables** in Render dashboard
2. **Monitor Deployment Logs** for specific error messages
3. **Test Locally** with production settings
4. **Update Configuration** based on error messages

## Current Files Structure
```
/
├── wsgi.py                    # Main entry point for Render
├── render.yaml               # Render deployment config
├── Procfile                  # Alternative deployment config
├── requirements.txt          # Python dependencies
└── gpo_product/
    ├── app.py               # Main Flask application
    ├── wsgi.py             # Alternative entry point
    ├── database.py         # Database configuration
    └── ...                 # Other application files
```

## Success Indicators
- ✅ Application starts without errors
- ✅ Database connection established
- ✅ HTTP 200 response on health check
- ✅ All routes accessible 