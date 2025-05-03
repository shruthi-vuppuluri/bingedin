#!/usr/bin/env bash

# Print environment info for debugging
echo "Starting application..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Run the application with gunicorn
echo "Running gunicorn with bingedin.wsgi:application"
gunicorn bingedin.wsgi:application --log-file - 