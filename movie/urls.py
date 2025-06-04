from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movie_list, name='movie_list'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('movie/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('movie/<slug:movie_slug>/book/', views.book_ticket, name='book_ticket'),
    path('loyalty/', views.loyalty_dashboard, name='loyalty_dashboard'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
