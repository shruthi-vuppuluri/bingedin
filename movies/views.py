from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
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
    
    # Enhanced recommendation system that considers genres, actors, and directors
    recommended_movies = []
    
    if hasattr(request.user, 'profile'):
        # Get user's watched and recommended movies to analyze preferences
        watched_movies = request.user.profile.watched_movies.all()
        user_recommended_movies = request.user.profile.recommended_movies.all()
        user_movies = list(watched_movies) + list(user_recommended_movies)
        
        # Extract favorite genres, actors, and directors from user's watched/recommended movies
        favorite_genres = []
        favorite_actors = []
        favorite_directors = []
        
        # Add explicitly set favorite genres from profile
        if request.user.profile.favorite_genres:
            favorite_genres.extend(request.user.profile.favorite_genres.split(','))
        
        # Extract preferences from user's movies
        for movie in user_movies:
            # Add movie genres
            for genre in movie.genres.all():
                if genre.name not in favorite_genres:
                    favorite_genres.append(genre.name)
            
            # Add movie actors (split by commas since actors field is a comma-separated string)
            if movie.actors:
                movie_actors = [actor.strip() for actor in movie.actors.split(',')]
                for actor in movie_actors:
                    if actor and actor not in favorite_actors:
                        favorite_actors.append(actor)
            
            # Add movie director
            if movie.director and movie.director not in favorite_directors:
                favorite_directors.append(movie.director)
        
        # Build recommendations based on genres, actors, and directors
        if favorite_genres or favorite_actors or favorite_directors:
            # First, find movies by favorite genres
            for genre_name in favorite_genres:
                genre_movies = Movie.objects.filter(genres__name__icontains=genre_name)
                for movie in genre_movies:
                    if movie not in recommended_movies and movie not in user_movies:
                        recommended_movies.append(movie)
            
            # Then, find movies by favorite actors
            for actor in favorite_actors:
                actor_movies = Movie.objects.filter(actors__icontains=actor)
                for movie in actor_movies:
                    if movie not in recommended_movies and movie not in user_movies:
                        recommended_movies.append(movie)
            
            # Finally, find movies by favorite directors
            for director in favorite_directors:
                director_movies = Movie.objects.filter(director__icontains=director)
                for movie in director_movies:
                    if movie not in recommended_movies and movie not in user_movies:
                        recommended_movies.append(movie)
    
    # If no recommendations based on preferences, show some popular ones
    if not recommended_movies:
        recommended_movies = recent_movies
    
    # Get featured movie, ensuring it has a valid ID
    featured_movie = recent_movies.first()
    
    context = {
        'featured_movie': featured_movie,
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
    
    # Enhanced recommendation system using Q objects
    
    # Create base queryset excluding current movie
    recommendations_query = Movie.objects.exclude(id=movie.id)
    
    # Build query conditions
    director_condition = Q(director__icontains=movie.director) if movie.director else Q()
    
    # Get actors from current movie
    actor_conditions = Q()
    if movie.actors:
        actors = [actor.strip() for actor in movie.actors.split(',')]
        for actor in actors:
            if actor:
                actor_conditions |= Q(actors__icontains=actor)
    
    # Find movies with matching genres
    genre_ids = movie.genres.values_list('id', flat=True)
    genre_matches = recommendations_query.filter(
        genres__id__in=genre_ids
    ).annotate(
        matching_genres=Count('genres', filter=Q(genres__id__in=genre_ids))
    ).filter(
        matching_genres__gte=1
    )
    
    # Combine recommendations, prioritizing movies that match multiple criteria
    similar_movies = []
    
    # First priority: movies matching director AND actor AND 2+ genres
    director_actor_genre_matches = genre_matches.filter(
        director_condition,
        actor_conditions,
        matching_genres__gte=2
    ).distinct()
    similar_movies.extend(list(director_actor_genre_matches)[:3])
    
    # Second priority: movies matching director OR actor AND 2+ genres
    if len(similar_movies) < 6:
        director_or_actor_genre_matches = genre_matches.filter(
            director_condition | actor_conditions,
            matching_genres__gte=2
        ).exclude(
            id__in=[m.id for m in similar_movies]
        ).distinct()
        similar_movies.extend(list(director_or_actor_genre_matches)[:6-len(similar_movies)])
    
    # Third priority: movies matching director OR actor
    if len(similar_movies) < 6:
        director_or_actor_matches = recommendations_query.filter(
            director_condition | actor_conditions
        ).exclude(
            id__in=[m.id for m in similar_movies]
        ).distinct()
        similar_movies.extend(list(director_or_actor_matches)[:6-len(similar_movies)])
    
    # Final priority: genre matches with at least one matching genre
    if len(similar_movies) < 6:
        remaining_genre_matches = genre_matches.exclude(
            id__in=[m.id for m in similar_movies]
        ).order_by('-matching_genres')
        similar_movies.extend(list(remaining_genre_matches)[:6-len(similar_movies)])
    
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

@login_required
def account_settings(request):
    user = request.user
    profile = user.profile
    
    # If POST request, update favorite genres
    if request.method == 'POST':
        # Update favorite genres
        favorite_genres = request.POST.get('favorite_genres', '')
        profile.favorite_genres = favorite_genres
        profile.save()
        
        # Update username if provided
        new_username = request.POST.get('username', '').strip()
        if new_username and new_username != user.username:
            from django.contrib.auth.models import User
            if not User.objects.filter(username=new_username).exists():
                user.username = new_username
                user.save()
                messages.success(request, "Username updated successfully.")
            else:
                messages.error(request, "Username already taken.")
        
        # Update email if provided
        new_email = request.POST.get('email', '').strip()
        if new_email and new_email != user.email:
            user.email = new_email
            user.save()
            messages.success(request, "Email updated successfully.")
        
        # Update password if provided
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        if new_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully. Please log in again.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
    
    # Get all available genres
    all_genres = Genre.objects.all()
    user_genres = profile.favorite_genres.split(',') if profile.favorite_genres else []
    
    context = {
        'user': user,
        'profile': profile,
        'all_genres': all_genres,
        'user_genres': user_genres,
    }
    
    return render(request, 'movies/account_settings.html', context)
