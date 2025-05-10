from django.urls import path
from django.contrib.auth import views as auth_views # Needed for default login/logout
from . import views

app_name = 'account' # Use Project 1's namespace 'account'

urlpatterns = [
    # User authentication (using Django's built-in views)
    path('login/', auth_views.LoginView.as_view(), name='login'), # Need to define a template later
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Add placeholder for signup, profile, watchlist urls required by base.html
    path('signup/', views.signup_page, name='signup'), # Need to define this view/template later
    path('profile/', views.user_profile_page, name='user_profile_detail'), # Need this view/template later
    path('watchlist/add/<slug:movie_id>/', views.add_to_watchlist_action, name='add_to_watchlist'), # Need this view later
    path('watchlist/remove/<slug:movie_id>/', views.remove_from_watchlist_action, name='remove_from_watchlist'), # Need this view later
]