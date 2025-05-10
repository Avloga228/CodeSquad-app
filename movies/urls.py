from django.urls import path
from . import views

app_name = 'movies' # Add app namespace

urlpatterns = [
    # Project 1 had movie_list at '', but let's put our homepage here for now
    path('', views.home_page, name='home_page'), # Temporary home view

    # Pages from P1 header nav
    path('popular/', views.popular_movies_page, name='popular_movies_list'),
    path('new-movies/', views.new_movies_page, name='new_movies_list'),
    path('tv-series/', views.tv_series_page, name='tv_series_list'),

    # Add placeholder for movie detail page required by nav links
    path('movie/<slug:slug>/', views.movie_detail_page, name='movie_detail'),

    # Add other movie urls from Project 1 later if needed (create, update, delete)
    # path('create/', views.movie_create, name='movie_create'),
    # path('<slug:slug>/update/', views.movie_update, name='movie_update'),
    # path('<slug:slug>/delete/', views.movie_delete, name='movie_delete'),
]