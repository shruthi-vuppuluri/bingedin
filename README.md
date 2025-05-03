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

## Deployment on Render

This application is configured for easy deployment on Render:

1. Push this repository to GitHub
2. In Render dashboard, click "New Blueprint" 
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file and create the necessary services
5. Confirm the deployment settings and click "Apply"

The deployment will:
- Create a PostgreSQL database for your application
- Build and deploy your application
- Set up HTTPS automatically
- Run the initial migrations and static files collection

To update your deployment, simply push to your GitHub repository.

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