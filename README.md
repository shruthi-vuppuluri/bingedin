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

### Option 1: Using Blueprint (Recommended)
1. Push this repository to GitHub
2. In Render dashboard, click "New Blueprint" 
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file and create the necessary services
5. Confirm the deployment settings and click "Apply"

### Option 2: Manual Web Service
If Blueprint doesn't work, you can manually create a Web Service:
1. In Render dashboard, click "New Web Service"
2. Connect your GitHub repository
3. Configure with these settings:
   - Name: bingedin
   - Environment: Python
   - Region: Choose one close to your users
   - Branch: main (or your preferred branch)
   - Build Command: `./build.sh`
   - Start Command: `./start.sh`
   - Plan: Free
4. Add environment variables:
   - SECRET_KEY: (generate a secure random string)
   - DEBUG: false
   - OMDB_API_KEY: 651b75a9
5. Create a Postgres database and link it to your web service

### Note on the First Deployment
The first deployment might fail due to Render's default app.py expectations. If this happens:
1. After the first failed deployment, go to Dashboard > Web Service > Settings
2. Verify Start Command is `./start.sh` 
3. Click "Save Changes" and trigger a manual deploy

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