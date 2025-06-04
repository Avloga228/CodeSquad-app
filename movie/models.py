"""
This module defines the models for the cinema ticket booking system.

Models:
- Movie: Represents information about a movie
- CinemaHall: Represents a cinema hall with seats
- MovieSession: Represents a movie screening session
- Seat: Represents a seat in a cinema hall
- Booking: Represents a ticket booking
"""

from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone
import os
from django.core.exceptions import ValidationError

class Genre(models.Model):
    """
    Genre Model represents movie genres.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Movie(models.Model):
    """
    Movie Model represents information about a movie.

    Attributes:
    - title: The title of the movie
    - genres: The genres of the movie
    - release_date: The release date of the movie
    - description: Description or summary of the movie
    - directors: The directors of the movie
    - country: The country of the movie production
    - duration: Duration of the movie in minutes
    - poster: ImageField storing the movie's poster
    - horizontal_poster: ImageField storing the movie's horizontal poster
    - trailer_link: URLField storing the link to the movie's trailer
    - rating: Movie rating (0-10)
    - language: Movie language
    - created_at: Time the movie was posted
    - is_active: Whether the movie is currently active
    """
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    title = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='movies')
    release_date = models.DateField(default=timezone.now)
    description = models.TextField()
    directors = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, verbose_name='Duration in minutes')
    poster = models.ImageField(upload_to='movie_posters/', blank=True, null=True)
    horizontal_poster = models.ImageField(upload_to='movie_horizontal_posters/', blank=True, null=True)
    trailer_link = models.URLField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    language = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = orig = slugify(self.title)
            slug_exists = Movie.objects.filter(slug=base_slug).exclude(pk=self.pk).exists()

            count = 1
            while slug_exists:
                self.slug = f"{base_slug}-{count}"
                count += 1
                slug_exists = Movie.objects.filter(slug=self.slug).exclude(pk=self.pk).exists()
            else:
                self.slug = base_slug
            
        if self.poster:
            img = Image.open(self.poster)
            output = BytesIO()

            # Define the aspect ratio (2:3)
            target_ratio = 2 / 3
            width, height = img.size
            current_ratio = width / height

            if current_ratio > target_ratio:
                new_height = int(width / target_ratio)
                top = (height - new_height) / 2
                bottom = (height + new_height) / 2
                img = img.crop((0, top, width, bottom))
            elif current_ratio < target_ratio:
                new_width = int(height * target_ratio)
                left = (width - new_width) / 2
                right = (width + new_width) / 2
                img = img.crop((left, 0, right, height))

            max_size = (800, 1200)
            img.thumbnail(max_size)

            img.save(output, format='JPEG', quality=75)
            output.seek(0)

            self.poster.file = ContentFile(output.getvalue())

        super().save(*args, **kwargs)

        # Resize poster image if it exists
        if self.poster:
            img = Image.open(self.poster.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.poster.path)

class CinemaHall(models.Model):
    """
    CinemaHall Model represents a cinema hall with seats.

    Attributes:
    - name: Name of the hall
    - rows: Number of rows in the hall
    - seats_per_row: Number of seats per row
    """
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_per_row = models.IntegerField()

    def __str__(self):
        return f"{self.name}"

class MovieSession(models.Model):
    """Model for movie watching sessions."""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions')
    hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        unique_together = ['movie', 'hall', 'date', 'time']

    def __str__(self):
        return f"{self.movie.title} - {self.hall.name} - {self.date} {self.time}"

    def get_booked_seats_list(self):
        """Returns a list of all booked seat identifiers (e.g., ['1-5', '1-6']) for this session."""
        print(f"\nDebugging get_booked_seats_list for session {self.id}:")
        print(f"Session details: {self.movie.title} - {self.date} {self.time}")
        
        # Get all bookings for this session
        all_bookings = self.bookings.all()
        print(f"Total bookings found: {all_bookings.count()}")
        
        booked_seats = []
        # Only consider confirmed bookings
        confirmed_bookings = self.bookings.filter(status='confirmed')
        print(f"Confirmed bookings found: {confirmed_bookings.count()}")
        
        for booking in confirmed_bookings:
            print(f"Booking {booking.id}:")
            print(f"  - Status: {booking.status}")
            print(f"  - Booked seats: {booking.booked_seats}")
            if booking.booked_seats:
                booked_seats.extend(booking.booked_seats)
        
        print(f"Final booked seats list: {booked_seats}\n")
        return booked_seats

    def get_available_seats(self):
        """Returns the number of available seats for this session."""
        booked_count = len(self.get_booked_seats_list())
        return self.hall.rows * self.hall.seats_per_row - booked_count
    get_available_seats.short_description = 'Available Seats'

    def get_seat_status(self):
        """Returns a dictionary of seat statuses."""
        # Get booked seats once
        booked_seats = self.get_booked_seats_list()
        print(f"Session {self.id} - Booked seats: {booked_seats}")  # Single debug log per session
        
        # Create status dictionary
        status_dict = {}
        for row in range(1, self.hall.rows + 1):
            for seat_num in range(1, self.hall.seats_per_row + 1):
                seat_id = f"{row}-{seat_num}"
                status_dict[seat_id] = 'booked' if seat_id in booked_seats else 'available'
        
        return status_dict

class Booking(models.Model):
    """
    Booking Model represents a ticket booking.

    Attributes:
    - user: ForeignKey to User model
    - session: ForeignKey to MovieSession model
    - booked_seats: JSONField storing a list of booked seats (e.g., ["1-5", "1-6"])
    - total_price: Total price of the booking
    - booking_date: Date and time of the booking
    - status: Status of the booking (pending, confirmed, cancelled)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(MovieSession, on_delete=models.CASCADE, related_name='bookings')
    booked_seats = models.JSONField(default=list)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.session.movie.title}"

    class Meta:
        ordering = ['-booking_date']

class HomepageSettings(models.Model):
    """Model for managing homepage content settings."""
    name = models.CharField(max_length=100, default='Homepage Settings')
    
    # Featured movies for carousel
    featured_movies = models.ManyToManyField(
        Movie,
        related_name='featured_on_homepage',
        limit_choices_to={'is_active': True},
        blank=True
    )
    
    # Now playing section
    now_playing_movies = models.ManyToManyField(
        Movie,
        related_name='now_playing_on_homepage',
        limit_choices_to={'is_active': True, 'release_date__lte': timezone.now().date()},
        blank=True
    )
    
    # Coming soon section
    coming_soon_movies = models.ManyToManyField(
        Movie,
        related_name='coming_soon_on_homepage',
        limit_choices_to={'is_active': True, 'release_date__gt': timezone.now().date()},
        blank=True
    )
    
    # Top rated movies section
    top_rated_movies = models.ManyToManyField(
        Movie,
        related_name='top_rated_on_homepage',
        limit_choices_to={'is_active': True},
        blank=True
    )
    
    class Meta:
        verbose_name = 'Homepage Settings'
        verbose_name_plural = 'Homepage Settings'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and HomepageSettings.objects.exists():
            raise ValidationError('There can be only one HomepageSettings instance')
        return super().save(*args, **kwargs)

class LoyaltyTier(models.Model):
    """
    LoyaltyTier Model represents different membership tiers in the loyalty program.
    """
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ]

    name = models.CharField(max_length=20, choices=TIER_CHOICES)
    points_required = models.PositiveIntegerField()
    discount_percentage = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name.title()} - {self.discount_percentage}% discount"

    class Meta:
        ordering = ['points_required']

class UserLoyalty(models.Model):
    """
    UserLoyalty Model tracks user's loyalty points and tier.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty')
    points = models.PositiveIntegerField(default=0)
    tier = models.ForeignKey(LoyaltyTier, on_delete=models.SET_NULL, null=True, related_name='users')
    last_updated = models.DateTimeField(auto_now=True)
    total_earned_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s loyalty status"

    def update_tier(self):
        """Update user's tier based on their total earned points."""
        new_tier = LoyaltyTier.objects.filter(points_required__lte=self.total_earned_points).order_by('-points_required').first()
        if new_tier != self.tier:
            self.tier = new_tier
            self.save()

    def add_points(self, amount):
        """Add points and update tier."""
        self.points += amount
        self.total_earned_points += amount
        self.save()
        self.update_tier()

class PointTransaction(models.Model):
    """
    PointTransaction Model tracks all point transactions.
    """
    TRANSACTION_TYPES = [
        ('earn', 'Points Earned'),
        ('spend', 'Points Spent'),
    ]

    user_loyalty = models.ForeignKey('UserLoyalty', on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()  # Can be negative for spending
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, related_name='point_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_loyalty.user.username} - {self.transaction_type} {abs(self.amount)} points"
