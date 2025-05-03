#!/usr/bin/env bash

# Print environment info for debugging
echo "Starting application..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Check database connection and tables before starting
echo "Checking database status..."
python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingedin.settings')
django.setup()
from django.db import connections, connection
from django.db.utils import OperationalError

# Check connection
conn = connections['default']
try:
    conn.cursor()
    print('✅ Database connection successful')
    
    # Check if auth_user table exists
    cursor = connection.cursor()
    cursor.execute(\"\"\"
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='auth_user'
        UNION
        SELECT tablename FROM pg_catalog.pg_tables
        WHERE schemaname='public' AND tablename='auth_user'
    \"\"\")
    
    if cursor.fetchone():
        print('✅ auth_user table exists')
    else:
        print('❌ auth_user table missing! Running migrations...')
        import subprocess
        subprocess.run(['python', 'manage.py', 'migrate', '--verbosity', '2'])
        
except OperationalError as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

# Run migrations just to be safe
echo "Running migrations on startup to ensure database is up to date..."
python manage.py migrate --no-input || echo "Warning: Migrations failed, but continuing..."

# Initialize test data if needed
echo "Running data initialization script..."
python initialize_data.py || echo "Warning: Data initialization failed, but continuing..."

# Run the application with gunicorn
echo "Running gunicorn with bingedin.wsgi:application"
gunicorn bingedin.wsgi:application --log-file - 