#!/bin/bash

# Exit on error
set -e

# Check if the source .env file exists in the parent directory
if [ -f "../.env" ]; then
    echo "Copying .env file from parent directory..."
    cp ../.env ./.env
    echo "Environment variables copied successfully!"
else
    echo "No .env file found in the parent directory."
    echo "Please create a .env file with the following variables:"
    echo "SUPABASE_URL, SUPABASE_PASSWORD, SUPABASE_HOST, SUPABASE_PORT, SUPABASE_DB, SUPABASE_USER"
    echo "SECRET_KEY, FLASK_ENV, LLM_API_KEY"
fi 