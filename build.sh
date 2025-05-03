#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Make start script executable
chmod +x start.sh
echo "Made start.sh executable"

# Create a virtual environment if not running in one already
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Installing virtualenv package..."
    pip install virtualenv

    echo "Creating virtual environment..."
    python -m virtualenv env || python -m venv env

    echo "Activating virtual environment..."
    source env/bin/activate
fi

# Install python dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt || { echo "Failed to install from requirements.txt"; exit 1; }

# Install additional dependencies required for deployment
echo "Installing additional dependencies..."
pip install gunicorn dj-database-url psycopg2-binary whitenoise

# Create directories if they don't exist
echo "Setting up directories..."
mkdir -p staticfiles
mkdir -p static

# Check if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL is set. Using PostgreSQL for database."
else
    echo "WARNING: DATABASE_URL is not set. Using SQLite as fallback."
    # This is for local development, SQLite should work fine
fi

# Database check and info
echo "Database connection information:"
python -c "
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingedin.settings')
django.setup()
from django.db import connections
from django.db.utils import OperationalError
conn = connections['default']
try:
    conn.cursor()
    print('Database connection successful')
    print(f'Database engine: {connections.databases[\"default\"][\"ENGINE\"]}')
    if 'postgres' in connections.databases['default']['ENGINE']:
        print('Connected to PostgreSQL database')
    elif 'sqlite' in connections.databases['default']['ENGINE']:
        print('Connected to SQLite database')
except OperationalError as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input || { echo "Static collection failed but continuing..."; }

# Show available migrations
echo "Available migrations:"
python manage.py showmigrations

# Apply migrations with detailed output
echo "Applying database migrations..."
python manage.py migrate --plan  # Show what migrations would be applied
python manage.py migrate --verbosity 2 || { 
    echo "Migration failed! Retrying with setting creation..."; 
    
    # Create basic tables for auth if they don't exist
    echo "Creating basic auth tables..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingedin.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS auth_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOL NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOL NOT NULL,
    is_active BOOL NOT NULL,
    date_joined DATETIME NOT NULL
)
''')
print('Created auth_user table if it did not exist')
"
    # Try migrations again
    python manage.py migrate --verbosity 2
}

# Load initial data
echo "Loading initial movie data..."
python manage.py load_movies || { echo "Loading initial data failed but continuing..."; }

echo "Build process completed." 