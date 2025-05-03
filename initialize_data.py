#!/usr/bin/env python3
"""
Initialize database with test data and users.
Run this script after migrations to ensure you have working data in your database.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingedin.settings')
django.setup()

# Now import Django modules
from django.contrib.auth.models import User
from django.db import connections, connection
from django.core.management import call_command
from django.db.utils import OperationalError

def main():
    print("Initializing test data...")
    
    # Check database connection
    try:
        connection.ensure_connection()
        print("✅ Database connection successful")
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check if auth_user table exists
    try:
        # This will raise an exception if the table doesn't exist
        User.objects.count()
        print("✅ User table exists")
    except:
        print("❌ User table doesn't exist. Running migrations...")
        call_command('migrate')
    
    # Create test user if none exists
    if User.objects.count() == 0:
        print("Creating test user...")
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        print("✅ Created test user 'testuser' with password 'password123'")
    else:
        print(f"✅ {User.objects.count()} users already exist in database")
    
    # Load movie data
    try:
        from movies.models import Movie
        if Movie.objects.count() == 0:
            print("Loading movie data...")
            call_command('load_movies')
            print(f"✅ Loaded {Movie.objects.count()} movies")
        else:
            print(f"✅ {Movie.objects.count()} movies already exist in database")
    except Exception as e:
        print(f"❌ Error loading movies: {e}")
    
    print("Initialization complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 