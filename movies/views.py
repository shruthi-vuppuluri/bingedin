from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from .models import Movie, Genre, Review
from .forms import ReviewForm

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
    
    # Get all reviews for this movie
    reviews = movie.reviews.all()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Check if current user has already reviewed this movie
    user_review = None
    review_form = None
    
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        
        # If POST request, process the review form
        if request.method == 'POST':
            # If user already has a review, update it
            if user_review:
                review_form = ReviewForm(request.POST, instance=user_review)
            else:
                review_form = ReviewForm(request.POST)
                
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.movie = movie
                review.user = request.user
                review.save()
                messages.success(request, "Your review has been submitted!")
                return redirect('movie_detail', movie_id=movie_id)
        else:
            # If user already has a review, pre-populate the form
            if user_review:
                review_form = ReviewForm(instance=user_review)
            else:
                review_form = ReviewForm()
    
    context = {
        'movie': movie,
        'similar_movies': similar_movies,
        'is_watched': is_watched,
        'is_recommended': is_recommended,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'review_form': review_form,
    }
    
    return render(request, 'movies/movie_detail.html', context)

@login_required
def add_to_watched(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    # Check if movie is already in watched list
    already_exists = profile.watched_movies.filter(id=movie_id).exists()
    if already_exists:
        message = f"'{movie.title}' is already in your watched list!"
        message_type = 'info'
    else:
        profile.watched_movies.add(movie)
        message = f"'{movie.title}' added to your watched list!"
        message_type = 'success'
    
    # Show message only for non-AJAX requests
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if message_type == 'info':
            messages.info(request, message)
        else:
            messages.success(request, message)
    
    # Always return JSON for AJAX and redirect for regular requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_watched': True,
            'message': message
        })
    
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def add_to_recommended(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    # Check if movie is already in recommended list
    already_exists = profile.recommended_movies.filter(id=movie_id).exists()
    if already_exists:
        message = f"'{movie.title}' is already in your recommended list!"
        message_type = 'info'
    else:
        profile.recommended_movies.add(movie)
        message = f"'{movie.title}' added to your recommended list!"
        message_type = 'success'
    
    # Show message only for non-AJAX requests
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if message_type == 'info':
            messages.info(request, message)
        else:
            messages.success(request, message)
    
    # Always return JSON for AJAX and redirect for regular requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_recommended': True,
            'message': message
        })
    
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    
    # Check if the logged-in user is the owner of the review
    if review.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this review.")
    
    movie_id = review.movie.id
    review.delete()
    messages.success(request, "Your review has been deleted!")
    
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def remove_from_watched(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    # Check if movie is in the watched list
    if profile.watched_movies.filter(id=movie_id).exists():
        profile.watched_movies.remove(movie)
        message = f"'{movie.title}' removed from your watched list."
        message_type = 'success'
    else:
        message = f"'{movie.title}' is not in your watched list."
        message_type = 'info'
    
    # Show message only for non-AJAX requests
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if message_type == 'info':
            messages.info(request, message)
        else:
            messages.success(request, message)
    
    # Always return JSON for AJAX and redirect for regular requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_watched': False,
            'message': message
        })
    
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def remove_from_recommended(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile = request.user.profile
    
    # Check if movie is in the recommended list
    if profile.recommended_movies.filter(id=movie_id).exists():
        profile.recommended_movies.remove(movie)
        message = f"'{movie.title}' removed from your recommended list."
        message_type = 'success'
    else:
        message = f"'{movie.title}' is not in your recommended list."
        message_type = 'info'
    
    # Show message only for non-AJAX requests
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if message_type == 'info':
            messages.info(request, message)
        else:
            messages.success(request, message)
    
    # Always return JSON for AJAX and redirect for regular requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_recommended': False,
            'message': message
        })
    
    return redirect('movie_detail', movie_id=movie_id)
