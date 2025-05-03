from django.core.management.base import BaseCommand
from movies.models import Movie, Genre
import random
import requests
import time
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Loads initial movie data'

    def handle(self, *args, **kwargs):
        # Create genres
        genre_names = ['Romance', 'Action & Adventure', 'Horror & Thriller', 'Crime & Mystery', 'Drama', 'Comedy']
        genres = {}
        
        for name in genre_names:
            genre, created = Genre.objects.get_or_create(name=name)
            genres[name] = genre
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created genre: {name}'))
        
        # Movie data with dynamic poster URLs from OMDb
        movies_data = [
            {
                'title': 'The History of Sound',
                'description': 'Two music students form a deep bond while collecting folk songs during WWI.',
                'actors': 'Paul Mescal, Josh O\'Connor',
                'director': 'Oliver Hermanus',
                'release_year': 2025,
                'genres': ['Romance', 'Drama'],
            },
            {
                'title': 'Materialists',
                'description': 'A matchmaker reevaluates her views on love when caught between two suitors.',
                'actors': 'Dakota Johnson, Pedro Pascal',
                'director': 'Celine Song',
                'release_year': 2025,
                'genres': ['Romance', 'Comedy'],
            },
            {
                'title': 'Red, White & Royal Blue',
                'description': 'The son of the U.S. president and a British prince navigate a secret romance.',
                'actors': 'Taylor Zakhar Perez, Nicholas Galitzine',
                'director': 'Matthew López',
                'release_year': 2023,
                'genres': ['Romance', 'Comedy'],
            },
            {
                'title': 'Love at First Sight',
                'description': 'Strangers connect during a flight, leading to unexpected romance.',
                'actors': 'Haley Lu Richardson, Ben Hardy',
                'director': 'Vanessa Caswill',
                'release_year': 2023,
                'genres': ['Romance'],
            },
            {
                'title': 'Your Place or Mine',
                'description': 'Two best friends swap homes and lives, discovering new perspectives.',
                'actors': 'Reese Witherspoon, Ashton Kutcher',
                'director': 'Aline Brosh McKenna',
                'release_year': 2023,
                'genres': ['Romance', 'Comedy'],
            },
            {
                'title': 'Anyone But You',
                'description': 'Exes pretend to be a couple during a destination wedding.',
                'actors': 'Sydney Sweeney, Glen Powell',
                'director': 'Will Gluck',
                'release_year': 2023,
                'genres': ['Romance', 'Comedy'],
            },
            {
                'title': 'The Idea of You',
                'description': 'A 40-year-old woman falls for a younger pop star.',
                'actors': 'Anne Hathaway, Nicholas Galitzine',
                'director': 'Michael Showalter',
                'release_year': 2024,
                'genres': ['Romance'],
            },
            {
                'title': 'Havoc',
                'description': 'A fixer battles gangs and corrupt cops to rescue a kidnapped boy.',
                'actors': 'Tom Hardy',
                'director': 'Gareth Evans',
                'release_year': 2025,
                'genres': ['Action & Adventure', 'Crime & Mystery'],
            },
            {
                'title': 'Thunderbolts',
                'description': 'Disgraced MCU characters unite for a mission filled with redemption.',
                'actors': 'Florence Pugh, David Harbour',
                'director': 'Jake Schreier',
                'release_year': 2025,
                'genres': ['Action & Adventure'],
            },
            {
                'title': 'Mission: Impossible – Dead Reckoning Part One',
                'description': 'Ethan Hunt faces a rogue AI threatening global security.',
                'actors': 'Tom Cruise',
                'director': 'Christopher McQuarrie',
                'release_year': 2023,
                'genres': ['Action & Adventure'],
            },
            {
                'title': 'John Wick: Chapter 4',
                'description': 'John Wick uncovers a path to defeating The High Table.',
                'actors': 'Keanu Reeves',
                'director': 'Chad Stahelski',
                'release_year': 2023,
                'genres': ['Action & Adventure', 'Crime & Mystery'],
            },
            {
                'title': 'Extraction 2',
                'description': 'Tyler Rake returns for another high-stakes rescue mission.',
                'actors': 'Chris Hemsworth',
                'director': 'Sam Hargrave',
                'release_year': 2023,
                'genres': ['Action & Adventure'],
            },
            {
                'title': 'The Gray Man',
                'description': 'A CIA operative becomes a target after uncovering secrets.',
                'actors': 'Ryan Gosling, Chris Evans',
                'director': 'Anthony and Joe Russo',
                'release_year': 2022,
                'genres': ['Action & Adventure', 'Crime & Mystery'],
            },
            {
                'title': 'Late Night with the Devil',
                'description': 'A 1970s talk show host invites a possessed girl on air, leading to terrifying consequences.',
                'actors': 'David Dastmalchian',
                'director': 'Colin & Cameron Cairnes',
                'release_year': 2024,
                'genres': ['Horror & Thriller'],
            },
            {
                'title': 'In a Violent Nature',
                'description': 'A slasher film told from the killer\'s perspective as he hunts down victims in a forest.',
                'actors': 'Ry Barrett',
                'director': 'Chris Nash',
                'release_year': 2024,
                'genres': ['Horror & Thriller'],
            },
            {
                'title': 'Evil Dead Rise',
                'description': 'Two estranged sisters face off against flesh-possessing demons in a high-rise building.',
                'actors': 'Lily Sullivan, Alyssa Sutherland',
                'director': 'Lee Cronin',
                'release_year': 2023,
                'genres': ['Horror & Thriller'],
            },
            {
                'title': 'The Nun II',
                'description': 'Sister Irene returns to confront the demonic force Valak in 1950s France.',
                'actors': 'Taissa Farmiga',
                'director': 'Michael Chaves',
                'release_year': 2023,
                'genres': ['Horror & Thriller'],
            },
            {
                'title': 'Talk to Me',
                'description': 'Teenagers discover a way to conjure spirits using an embalmed hand, leading to horrifying consequences.',
                'actors': 'Sophie Wilde',
                'director': 'Danny & Michael Philippou',
                'release_year': 2022,
                'genres': ['Horror & Thriller'],
            },
            {
                'title': 'The Black Phone',
                'description': 'A kidnapped boy communicates with past victims through a mysterious phone to escape his captor.',
                'actors': 'Mason Thames, Ethan Hawke',
                'director': 'Scott Derrickson',
                'release_year': 2021,
                'genres': ['Horror & Thriller', 'Crime & Mystery'],
            },
            {
                'title': 'The Killer',
                'description': 'An assassin embarks on a global vendetta after a hit goes wrong.',
                'actors': 'Michael Fassbender',
                'director': 'David Fincher',
                'release_year': 2023,
                'genres': ['Crime & Mystery', 'Action & Adventure'],
            },
            {
                'title': 'Black Bag',
                'description': 'A spy thriller where a CIA operative uncovers a conspiracy that threatens global security.',
                'actors': 'Cate Blanchett, Michael Fassbender',
                'director': 'Steven Soderbergh',
                'release_year': 2025,
                'genres': ['Crime & Mystery', 'Action & Adventure'],
            },
            {
                'title': 'The Buckingham Murders',
                'description': 'A British-Indian detective investigates the murder of a child in Buckinghamshire.',
                'actors': 'Kareena Kapoor Khan',
                'director': 'Hansal Mehta',
                'release_year': 2023,
                'genres': ['Crime & Mystery'],
            },
            {
                'title': 'Reptile',
                'description': 'A detective uncovers a complex web of deception while investigating a brutal murder.',
                'actors': 'Benicio Del Toro, Justin Timberlake',
                'director': 'Grant Singer',
                'release_year': 2023,
                'genres': ['Crime & Mystery'],
            },
            {
                'title': 'Prisoners',
                'description': 'When Keller Dover\'s daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads.',
                'actors': 'Hugh Jackman, Jake Gyllenhaal',
                'director': 'Denis Villeneuve',
                'release_year': 2013,
                'genres': ['Crime & Mystery', 'Drama'],
            },
            {
                'title': 'Dune: Part Two',
                'description': 'Paul Atreides unites with the Fremen to avenge his family.',
                'actors': 'Timothée Chalamet',
                'director': 'Denis Villeneuve',
                'release_year': 2024,
                'genres': ['Action & Adventure', 'Drama'],
            },
            {
                'title': 'Past Lives',
                'description': 'Childhood friends reunite, questioning destiny and choices.',
                'actors': 'Greta Lee, Teo Yoo',
                'director': 'Celine Song',
                'release_year': 2023,
                'genres': ['Romance', 'Drama'],
            },
            {
                'title': 'The Little Things',
                'description': 'Deputy Sheriff Deke teams with Sgt. Baxter to search for a serial killer who\'s terrorizing Los Angeles.',
                'actors': 'Denzel Washington, Rami Malek',
                'director': 'John Lee Hancock',
                'release_year': 2021,
                'genres': ['Crime & Mystery', 'Drama'],
            },
        ]
        
        # OMDb API token
        omdb_api_key = '651b75a9'
        
        # Custom placeholder image URL - using our SVG placeholder
        placeholder_image_url = f"{settings.STATIC_URL}images/no_poster.svg"
        
        # Function to fetch movie poster from OMDb
        def fetch_movie_poster(title, year=None):
            base_url = 'http://www.omdbapi.com/'
            
            # Prepare parameters
            params = {
                'apikey': omdb_api_key,
                't': title,
                'type': 'movie'
            }
            
            if year:
                params['y'] = year
                
            try:
                response = requests.get(base_url, params=params)
                data = response.json()
                
                if data.get('Response') == 'True' and data.get('Poster') != 'N/A':
                    return data.get('Poster')
                else:
                    self.stdout.write(self.style.WARNING(f'No poster found for {title}'))
                    # Return our custom placeholder image
                    return placeholder_image_url
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fetching poster for {title}: {str(e)}'))
                return placeholder_image_url
        
        # Update all movies with posters from OMDb
        for movie in Movie.objects.all():
            poster_url = fetch_movie_poster(movie.title, movie.release_year)
            if poster_url:
                movie.image_url = poster_url
                movie.save()
                self.stdout.write(self.style.SUCCESS(f'Updated image for movie: {movie.title}'))
            time.sleep(0.2)  # Add a small delay to avoid hitting API rate limits
        
        # Load movies that don't exist yet
        for movie_data in movies_data:
            # Fetch poster from OMDb
            poster_url = fetch_movie_poster(movie_data['title'], movie_data.get('release_year'))
            movie_data['image_url'] = poster_url
            
            # Create the movie
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'actors': movie_data['actors'],
                    'director': movie_data['director'],
                    'release_year': movie_data['release_year'],
                    'image_url': movie_data['image_url'],
                }
            )
            
            # Add genres
            if created:
                for genre_name in movie_data['genres']:
                    movie.genres.add(genres[genre_name])
                self.stdout.write(self.style.SUCCESS(f'Created movie: {movie.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Movie already exists: {movie.title}'))
            
            time.sleep(0.2)  # Add a small delay to avoid hitting API rate limits
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded movie data with OMDb poster images')) 