"""
Contains view functions related to user profiles.

This module includes various view functions for managing user profiles,
such as displaying user profile details.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from movie.models import Movie, Booking
from .forms import UserProfileForm, SignUpForm

@login_required
def user_profile_detail(request):
    """
    View function to display a user's profile details and bookings.

    Args:
    - request: HTTP request object

    Returns:
    - Rendered HTML template with user profile details and bookings
    """
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        
        # Get the user's bookings
        user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

        context = {
            'user_profile': user_profile,
            'user_bookings': user_bookings,
        }
        return render(request, 'user_profile/detail.html', context)
    except UserProfile.DoesNotExist:
        raise Http404("User profile does not exist")

def signup(request):
    """
    Handle user signup.

    If the request method is POST, validate the form and create a new user.
    Redirect to the login page upon successful signup.
    If the request method is GET, display the signup form.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally, perform additional actions such as sending a welcome email or setting user attributes
            # e.g., user.send_welcome_email()
            return redirect('account:login')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'user_profile/signup.html', context)
