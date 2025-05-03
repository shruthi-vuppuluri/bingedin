#!/usr/bin/env bash

# Print environment info for debugging
echo "Starting application..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# If running on Render, always run migrations first
if [ "$RENDER" = "true" ]; then
    echo "Running on Render with in-memory SQLite database"
    echo "Tables need to be created on every restart"
    
    # Apply migrations to create database schema
    echo "Running migrations (tables must be created on every startup with in-memory database)..."
    python manage.py migrate --noinput

    # Run the data initialization script to create a test user and load movies
    echo "Running data initialization script..."
    python initialize_data.py
    
    echo "Database initialization complete!"
else
    echo "Running in development mode"
    
    # Only run migrations if needed
    echo "Checking if migrations are needed..."
    python manage.py migrate --plan | grep -q "No planned migration operations" || python manage.py migrate --noinput
fi

# Run the application with gunicorn
echo "Running gunicorn with bingedin.wsgi:application"
gunicorn bingedin.wsgi:application --log-file - 