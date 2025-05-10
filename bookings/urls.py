from django.urls import path
from . import views

app_name = 'bookings' # Add app namespace

urlpatterns = [
    path('', views.pricing_page, name='subscriptions_list'), # Repurposing the name
    # Add other booking/checkout urls later
]