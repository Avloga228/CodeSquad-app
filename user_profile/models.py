"""
Module: user_profile.py
Description: Contains the UserProfile model for user profiles.
"""

from django.db import models
from django.contrib.auth.models import User
from movie.models import Movie

class UserProfile(models.Model):
    """
    Represents a user profile in the application.

    Attributes:
    - user (User): One-to-one relationship with the User model from Django's auth system.
    # Add other fields related to user profile
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
