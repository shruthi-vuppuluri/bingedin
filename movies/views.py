from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Movie, Genre

# Create your views here.

@login_required
def home(request):
    # Get all the genres
    genres = Genre.objects.all().prefetch_related('movies')
    
    # Get recent movies (simulating "trending" for demonstration)
    recent_movies = Movie.objects.all().order_by('-id')[:10]
    
    # Basic recommendation: show movies based on the user's favorite genres
    # In a real application, you would use a more sophisticated recommendation algorithm
    recommended_movies = []
    if hasattr(request.user, 'profile') and request.user.profile.favorite_genres:
        favorite_genres = request.user.profile.favorite_genres.split(',')
        for genre_name in favorite_genres:
            genre_movies = Movie.objects.filter(genres__name__icontains=genre_name)
            recommended_movies.extend(genre_movies)
    
    # If no recommendations based on favorites, show some popular ones
    if not recommended_movies:
        recommended_movies = recent_movies
    
    context = {
        'featured_movie': recent_movies.first(),  # Featured movie for the hero section
        'genres': genres,
        'recommended_movies': recommended_movies[:10],
        'recent_movies': recent_movies,
    }
    
    return render(request, 'movies/home.html', context)

@login_required
def search(request):
    query = request.GET.get('q', '')
    
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(actors__icontains=query) |
            Q(director__icontains=query)
        )
    else:
        movies = Movie.objects.none()
    
    # Get recent movies for the Popular Movies section
    recent_movies = Movie.objects.all().order_by('-id')[:12]
    
    context = {
        'query': query,
        'movies': movies,
        'recent_movies': recent_movies,
    }
    
    return render(request, 'movies/search.html', context)

@login_required
def profile(request):
    watched_movies = request.user.profile.watched_movies.all()
    recommended_movies = request.user.profile.recommended_movies.all()
    
    context = {
        'user': request.user,
        'watched_movies': watched_movies,
        'recommended_movies': recommended_movies,
    }
    
    return render(request, 'movies/profile.html', context)

@login_required
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    # Get similar movies (based on genres)
    similar_movies = Movie.objects.filter(genres__in=movie.genres.all()).exclude(id=movie.id).distinct()[:6]
    
    # Check if movie is in user's watched list
    is_watched = request.user.profile.watched_movies.filter(id=movie_id).exists()
    
    # Check if movie is in user's recommended list
    is_recommended = request.user.profile.recommended_movies.filter(id=movie_id).exists()
    
    context = {
        'movie': movie,
        'similar_movies': similar_movies,
        'is_watched': is_watched,
        'is_recommended': is_recommended,
    }
    
    return render(request, 'movies/movie_detail.html', context)

@login_required
def add_to_watched(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    # Check if movie is already in watched list
    if profile.watched_movies.filter(id=movie_id).exists():
        messages.info(request, f"'{movie.title}' is already in your watched list!")
    else:
        profile.watched_movies.add(movie)
        messages.success(request, f"'{movie.title}' added to your watched list!")
    
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def add_to_recommended(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    # Check if movie is already in recommended list
    if profile.recommended_movies.filter(id=movie_id).exists():
        messages.info(request, f"'{movie.title}' is already in your recommended list!")
    else:
        profile.recommended_movies.add(movie)
        messages.success(request, f"'{movie.title}' added to your recommended list!")
    
    return redirect('movie_detail', movie_id=movie_id)
