from django.db import models

# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.IntegerField()
    actors = models.CharField(max_length=200)
    director = models.CharField(max_length=100)
    genres = models.ManyToManyField(Genre, related_name='movies')
    image_url = models.URLField(default="https://via.placeholder.com/200x120")
    
    def __str__(self):
        return self.title
