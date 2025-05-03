from django.contrib import admin
from .models import Movie, Genre

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'director')
    list_filter = ('release_year', 'genres')
    search_fields = ('title', 'description', 'actors', 'director')
    filter_horizontal = ('genres',)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
