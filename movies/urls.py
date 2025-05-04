from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.account_settings, name='account_settings'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/add-to-watched/', views.add_to_watched, name='add_to_watched'),
    path('movie/<int:movie_id>/add-to-recommended/', views.add_to_recommended, name='add_to_recommended'),
    path('movie/<int:movie_id>/remove-from-watched/', views.remove_from_watched, name='remove_from_watched'),
    path('movie/<int:movie_id>/remove-from-recommended/', views.remove_from_recommended, name='remove_from_recommended'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
] 