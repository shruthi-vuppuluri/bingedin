from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    watched_movies = models.ManyToManyField(Movie, related_name='watched_by', blank=True)
    recommended_movies = models.ManyToManyField(Movie, related_name='recommended_by', blank=True)
    favorite_genres = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
