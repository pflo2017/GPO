#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting GPO Application..."

# Set Flask environment
export FLASK_APP=app.py
export FLASK_ENV=production

# Wait for database to be ready (if needed)
echo "⏳ Checking database connection..."

# Initialize database tables
echo "🗄️  Initializing database..."
python -c "
from app import db
try:
    db.create_all()
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
"

# Start Gunicorn
echo "🔥 Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app 