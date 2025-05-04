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
from django.core.management import call_command
from django.db import connections, connection, transaction
from django.db.utils import OperationalError, IntegrityError

def check_table_exists(table_name):
    """Check if a specific table exists in the database."""
    cursor = connection.cursor()
    
    # Detect database type
    db_engine = connection.vendor
    
    if db_engine == 'sqlite':
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=%s
        """, [table_name])
    else:  # postgresql or other
        cursor.execute("""
            SELECT c.relname FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = %s AND n.nspname = 'public'
        """, [table_name])
    
    return cursor.fetchone() is not None

@transaction.atomic
def main():
    print("Initializing test data...")
    
    # Check database connection
    try:
        connection.ensure_connection()
        print("✅ Database connection successful")
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check if auth_user table exists, if not run migrations
    if not check_table_exists('auth_user'):
        print("❌ User table doesn't exist. Running migrations...")
        call_command('migrate', interactive=False)
    else:
        print("✅ User table exists")
    
    # Create test user if none exists
    try:
        if User.objects.count() == 0:
            print("Creating test users...")
            # Create a regular test user
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            print(f"✅ Created test user: username=testuser, password=password123")
            
            # Create an admin user
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            print(f"✅ Created admin user: username=admin, password=admin123")
        else:
            print(f"✅ {User.objects.count()} users already exist in database")
            # Print usernames for reference
            usernames = User.objects.values_list('username', flat=True)
            print(f"Existing users: {', '.join(usernames)}")
    except IntegrityError as e:
        print(f"⚠️ User creation error (may already exist): {e}")
    except Exception as e:
        print(f"❌ Error creating users: {e}")
    
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
    
    # Create user profiles if needed
    try:
        from accounts.models import UserProfile
        from django.db.models import Count
        
        # Find users without profiles
        users_without_profiles = User.objects.annotate(
            profile_count=Count('profile')
        ).filter(profile_count=0)
        
        if users_without_profiles.exists():
            print(f"Creating profiles for {users_without_profiles.count()} users...")
            for user in users_without_profiles:
                UserProfile.objects.create(user=user)
            print("✅ Created missing user profiles")
        else:
            print("✅ All users have profiles")
    except Exception as e:
        print(f"❌ Error creating user profiles: {e}")
    
    print("Initialization complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 