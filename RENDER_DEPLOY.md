# Deploying GPO to Render

This guide provides step-by-step instructions for deploying the Global Project Orchestrator (GPO) application to [Render](https://render.com).

## Prerequisites

1. A [Render](https://render.com) account
2. A [Supabase](https://supabase.com) account with a PostgreSQL database
3. Your GPO codebase in a Git repository (GitHub, GitLab, etc.)

## Deployment Steps

### 1. Set Up Your Supabase Database

1. Log in to your Supabase account
2. Create a new project or use an existing one
3. Navigate to the SQL Editor and run the schema creation scripts from `gpo_product/schema.sql`
4. Note down your database connection details:
   - Host
   - Port (usually 5432 or 6543)
   - Database name (usually "postgres")
   - Username
   - Password

### 2. Deploy to Render

#### Option 1: Deploy via Dashboard

1. Log in to your Render account
2. Click "New" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `gpo-cloud-gpo` (or your preferred name)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variables:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: (generate a secure random string)
   - `SUPABASE_HOST`: (your Supabase host)
   - `SUPABASE_DB`: `postgres` (or your database name)
   - `SUPABASE_USER`: (your Supabase username)
   - `SUPABASE_PASSWORD`: (your Supabase password)
   - `SUPABASE_PORT`: `5432` (or your Supabase port)
6. Click "Create Web Service"

#### Option 2: Deploy via render.yaml

1. Make sure your repository contains the `render.yaml` file
2. Log in to your Render account
3. Click "New" and select "Blueprint"
4. Connect your Git repository
5. Render will automatically detect the `render.yaml` file
6. Update the environment variables as prompted
7. Click "Apply"

### 3. Verify Deployment

1. Wait for the deployment to complete
2. Click on the generated URL to access your application
3. If you encounter any issues, check the logs in the Render dashboard

## Troubleshooting

### Common Issues

#### Database Connection Errors

If you see database connection errors in the logs:

1. Verify your Supabase credentials
2. Check if your IP is allowlisted in Supabase
3. Ensure the database exists and has the correct schema

#### Import Errors

If you see Python import errors:

1. Check that all dependencies are in `requirements.txt`
2. Verify the file structure matches the imports
3. Run the `deployment_test.py` script locally to identify issues

#### Application Startup Errors

If the application fails to start:

1. Check the Render logs for specific error messages
2. Verify that `app.py` is in the root directory
3. Ensure the `gunicorn` command is correctly specified

## Maintenance

### Updating Your Deployment

1. Push changes to your Git repository
2. Render will automatically deploy the changes if auto-deploy is enabled
3. Otherwise, manually trigger a deploy from the Render dashboard

### Monitoring

1. Use the Render dashboard to monitor your application
2. Check logs for errors or warnings
3. Set up alerts for critical issues

## Support

If you encounter issues not covered in this guide:

1. Check the [Render documentation](https://render.com/docs)
2. Review the [GPO documentation](./README.md)
3. Contact support for assistance 