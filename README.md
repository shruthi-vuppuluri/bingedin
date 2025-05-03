# BingedIn

A Django application for tracking movies and TV shows.

## Features

- Browse movies by genre
- View movie details including cast, director, and release year
- Initial data loading with movie posters from OMDb API

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Apply migrations: `python manage.py migrate`
4. Load initial movie data: `python manage.py load_movies`
5. Run the server: `python manage.py runserver`

## Technologies Used

- Django
- SQLite
- HTML/CSS
- JavaScript

## Project Structure

- `accounts/`: User authentication and profile management
- `movies/`: Movie models, views, and recommendation logic
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)

## Credits

This project was created as a demonstration of a movie recommendation platform inspired by Netflix.

## License

This project is open-source and available under the MIT License. 