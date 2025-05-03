#!/bin/bash

echo "Making migrations..."
python3 manage.py makemigrations

echo "Applying migrations..."
python3 manage.py migrate

echo "Loading initial movie data..."
python3 manage.py load_movies

echo "Starting development server..."
python3 manage.py runserver 