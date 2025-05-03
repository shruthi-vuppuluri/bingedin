#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

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
pip install gunicorn dj-database-url psycopg2-binary whitenoise

# Create directories if they don't exist
echo "Setting up directories..."
mkdir -p staticfiles
mkdir -p static

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input || { echo "Static collection failed but continuing..."; }

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate || { echo "Migration failed but continuing..."; }

echo "Build process completed." 