from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_favorite_genres')
    filter_horizontal = ('watched_movies',)
    
    def display_favorite_genres(self, obj):
        return obj.favorite_genres
    
    display_favorite_genres.short_description = 'Favorite Genres'

admin.site.register(UserProfile, UserProfileAdmin)
