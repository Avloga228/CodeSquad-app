"""
This module contains views to perform CRUD operations on Movie model.

These views handle rendering a list of movies, displaying details of a specific movie,
creating new movies.

Functions:
- movie_list: Renders a list of movies with search and filters.
- movie_detail: Renders details of a specific movie based on its primary key.
- movie_create: Handles the creation of a new movie.
- book_ticket: Renders the ticket booking page for a specific movie.
- schedule_view: Renders the schedule page showing movie sessions for a selected date.
"""
from datetime import datetime
from itertools import zip_longest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.contrib import messages
from .forms import MovieForm
from review.forms import ReviewForm
from .models import Movie, Genre, HomepageSettings, MovieSession, Booking
from user_profile.models import UserProfile
from review.models import Review
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import UserLoyalty, LoyaltyTier, PointTransaction
from decimal import Decimal

def home(request):
    """Renders the home page with different movie categories."""
    # Get homepage settings
    settings = HomepageSettings.objects.first()
    if settings is None:
        settings = HomepageSettings.objects.create(name='Homepage Settings')

    # Get featured movies for carousel
    featured_movies = settings.featured_movies.all()[:3]
    if not featured_movies:
        # Fallback to default selection if no movies are selected
        featured_movies = Movie.objects.filter(
            is_active=True
        ).order_by('-rating', '-release_date')[:3]
    
    # Get now playing movies
    now_playing_movies = settings.now_playing_movies.all()[:4]
    if not now_playing_movies:
        # Fallback to default selection
        now_playing_movies = Movie.objects.filter(
            release_date__lte=timezone.now().date(),
            is_active=True
        ).order_by('-rating')[:4]
    
    # Get coming soon movies
    coming_soon_movies = settings.coming_soon_movies.all()[:4]
    if not coming_soon_movies:
        # Fallback to default selection
        coming_soon_movies = Movie.objects.filter(
            release_date__gt=timezone.now().date(),
            is_active=True
        ).order_by('release_date')[:4]
    
    # Get top rated movies
    top_rated_movies = settings.top_rated_movies.all()[:4]
    if not top_rated_movies:
        # Fallback to default selection
        top_rated_movies = Movie.objects.filter(
            is_active=True
        ).order_by('-rating')[:4]
    
    context = {
        'featured_movies': featured_movies,
        'now_playing_movies': now_playing_movies,
        'coming_soon_movies': coming_soon_movies,
        'top_rated_movies': top_rated_movies,
    }
    return render(request, 'movie/home.html', context)

def movie_list(request):
    """Renders a list of movies with search and filters."""
    movies_list = Movie.objects.filter(is_active=True)
    query = request.GET.get('q', '').strip()  # Strip whitespace and default to empty string
    selected_genre = request.GET.get('genre')
    selected_rating = request.GET.get('rating')
    sort_by = request.GET.get('sort', 'newest')
    
    # Search functionality - convert both title and query to lowercase for comparison
    if query:
        query_lower = query.lower()
        movies_list = [movie for movie in movies_list if query_lower in movie.title.lower()]
    
    # Genre filter
    if selected_genre:
        movies_list = [movie for movie in movies_list if selected_genre in [str(g.id) for g in movie.genres.all()]]
    
    # Rating filter
    if selected_rating:
        movies_list = [movie for movie in movies_list if movie.rating >= float(selected_rating)]
    
    # Sorting
    if sort_by == 'newest':
        movies_list = sorted(movies_list, key=lambda x: x.release_date, reverse=True)
    elif sort_by == 'oldest':
        movies_list = sorted(movies_list, key=lambda x: x.release_date)
    elif sort_by == 'rating':
        movies_list = sorted(movies_list, key=lambda x: x.rating, reverse=True)
    elif sort_by == 'title':
        movies_list = sorted(movies_list, key=lambda x: x.title)
    
    # Get all genres for the filter dropdown
    genres = Genre.objects.all()
    
    # Pagination
    paginator = Paginator(movies_list, 12)
    page = request.GET.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    context = {
        'movies': movies,
        'query': query,
        'genres': genres,
        'selected_genre': selected_genre,
        'selected_rating': selected_rating,
        'sort_by': sort_by,
    }
    return render(request, 'movie/movie_list.html', context)

def popular_movies(request):
    """Renders a list of popular movies."""
    popular_movies_list = Movie.objects.filter(
        is_active=True
    ).order_by('-rating')
    query = request.GET.get('q')
    
    if query:
        popular_movies_list = popular_movies_list.filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(description__icontains=query) |
            Q(directors__icontains=query) |
            Q(country__icontains=query)
        ).distinct()
        
    paginator = Paginator(popular_movies_list, 12)
    page = request.GET.get('page')

    try:
        popular_movies = paginator.page(page)
    except PageNotAnInteger:
        popular_movies = paginator.page(1)
    except EmptyPage:
        popular_movies = paginator.page(paginator.num_pages)
        
    context = {
        'popular_movies': popular_movies,
        'query': query,
    }
    return render(request, 'movie/most_popular.html', context)

def new_movies(request):
    """Renders a list of new movies."""
    now = timezone.now().date()
    new_movies_list = Movie.objects.filter(
        release_date__lte=now,
        is_active=True
    ).order_by('-release_date')
    query = request.GET.get('q')
    
    if query:
        new_movies_list = new_movies_list.filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(description__icontains=query) |
            Q(directors__icontains=query) |
            Q(country__icontains=query)
        ).distinct()
        
    paginator = Paginator(new_movies_list, 12)
    page = request.GET.get('page')

    try:
        new_movies = paginator.page(page)
    except PageNotAnInteger:
        new_movies = paginator.page(1)
    except EmptyPage:
        new_movies = paginator.page(paginator.num_pages)
        
    context = {
        'new_movies': new_movies,
        'query': query,
    }
    return render(request, 'movie/new_movies.html', context)

def movie_detail(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    reviews = Review.objects.filter(movie=movie)
    reviews_count = reviews.count()
    # Find related movies by genre instead of tags
    related_movies_by_genre = Movie.objects.filter(genres__in=movie.genres.all()).exclude(slug=slug).distinct()[:6]
    
    # Generating stars_list for reviews
    stars_list = []
    for review in reviews:
        rating = int(review.rating)
        stars = ['fa fa-star text-yellow-300' for _ in range(rating)]
        stars.extend(['fa fa-star text-gray-300 dark:text-gray-500' for _ in range(5 - rating)])
        stars_list.append(stars)

    # Zip reviews and stars_list together
    review_stars_zip = list(zip_longest(reviews, stars_list))
    
    # Handle review submission
    if request.method == 'POST':
        # Check if the user has already reviewed the movie
        existing_review = Review.objects.filter(movie=movie, user=request.user).exists()
        if existing_review:
            messages.error(request, 'You have already reviewed this movie.', extra_tags='error')
            return redirect('movies:movie_detail', slug=slug)
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user
            new_review.movie = movie
            new_review.save()

            messages.success(request, 'Your review has been successfully added!', extra_tags='success')
            
            return redirect('movies:movie_detail', slug=slug)
    else:
        form = ReviewForm()

    # Paginate reviews
    paginator = Paginator(reviews, 5)  # Show 5 reviews per page
    page_number = request.GET.get('page')
    try:
        paginated_reviews = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_reviews = paginator.page(1)
    except EmptyPage:
        paginated_reviews = paginator.page(paginator.num_pages)

    context = {
        'movie': movie,
        'reviews_count': reviews_count,
        'related_movies': related_movies_by_genre,
        'form': form,
        'paginated_reviews': paginated_reviews,
        'review_stars_zip': review_stars_zip,
    }
    return render(request, 'movie/movie_detail.html', context)

def movie_create(request):
    """Handles the creation of a new movie."""
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('movie_list')
        else:
            return render(request, 'movie/movie_form.html', {'form': form})
    else:
        form = MovieForm()
    return render(request, 'movie/movie_form.html', {'form': form})

@login_required
def loyalty_dashboard(request):
    """View for displaying user's loyalty program status and points."""
    user_loyalty, created = UserLoyalty.objects.get_or_create(user=request.user)
    
    # Get next tier information
    next_tier = LoyaltyTier.objects.filter(points_required__gt=user_loyalty.total_earned_points).order_by('points_required').first()
    points_to_next_tier = next_tier.points_required - user_loyalty.total_earned_points if next_tier else 0
    
    # Get recent transactions
    recent_transactions = user_loyalty.transactions.all().order_by('-created_at')[:5]
    
    context = {
        'user_loyalty': user_loyalty,
        'next_tier': next_tier,
        'points_to_next_tier': points_to_next_tier,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'movie/loyalty_dashboard.html', context)

def calculate_points_price(session_price):
    """Calculate the points price for a ticket (5x the money price)."""
    return int(float(session_price) * 5)

@login_required
def book_ticket(request, movie_slug):
    print(f"Request method: {request.method}")
    movie = get_object_or_404(Movie, slug=movie_slug)
    
    # Get all available dates for this movie
    available_dates = MovieSession.objects.filter(
        movie=movie,
        date__gte=timezone.now().date()
    ).values_list('date', flat=True).distinct().order_by('date')
    
    # Get selected date from query params or use first available date
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    elif available_dates:
        selected_date = available_dates[0]
    else:
        selected_date = None
    
    # Get available sessions for selected date, grouped by time
    sessions_for_date = {}
    if selected_date:
        all_sessions_on_date = MovieSession.objects.filter(
            movie=movie,
            date=selected_date
        ).order_by('time', 'hall__name')
        
        for session_obj in all_sessions_on_date:
            time_str = session_obj.time.strftime('%H:%M')
            if time_str not in sessions_for_date:
                sessions_for_date[time_str] = []
            sessions_for_date[time_str].append(session_obj)

    # Determine selected session based on session_id if provided
    selected_session_id = request.GET.get('session_id')
    session = None
    if selected_session_id:
        session = get_object_or_404(MovieSession, id=selected_session_id, movie=movie)
        # Ensure the selected session matches the selected date if date is also in params
        if selected_date and session.date != selected_date:
             # This scenario should ideally not happen with correct links, but good to handle
             session = None

    if request.method == 'POST' and session:
        print("Handling POST request...")
        selected_seats_str = request.POST.get('selected_seats')
        payment_method = request.POST.get('payment_method')
        print(f"Selected seats string: {selected_seats_str}")
        print(f"Payment method: {payment_method}")
        
        if selected_seats_str:
            selected_seats_list = selected_seats_str.split(',')
            print(f"Selected seats list: {selected_seats_list}")
            
            with transaction.atomic():
                # Get the list of already booked seats for this session
                already_booked_seats = session.get_booked_seats_list()
                
                # Check if any of the selected seats are already booked
                seats_to_book = []
                for seat_id in selected_seats_list:
                    if seat_id in already_booked_seats:
                        messages.error(request, f'Seat {seat_id} is already booked. Please select another seat.', extra_tags='error')
                        return redirect('movies:book_ticket', movie_slug=movie.slug)
                    seats_to_book.append(seat_id)

                # Calculate total price
                total_price = session.price * len(seats_to_book)

                # Get or create user loyalty at the start
                user_loyalty, created = UserLoyalty.objects.get_or_create(user=request.user)

                if payment_method == 'points':
                    # Check if user has enough points (using original price, no discount)
                    points_required = calculate_points_price(total_price)
                    if user_loyalty.points < points_required:
                        messages.error(request, 'Not enough points for this purchase.', extra_tags='error')
                        return redirect('movies:book_ticket', movie_slug=movie.slug)
                    
                    # Create booking with original price
                    booking = Booking.objects.create(
                        user=request.user,
                        session=session,
                        booked_seats=seats_to_book,
                        total_price=total_price,
                        status='confirmed'
                    )
                    
                    # Deduct points
                    user_loyalty.points -= points_required
                    user_loyalty.save()
                    
                    # Record point transaction
                    PointTransaction.objects.create(
                        user_loyalty=user_loyalty,
                        amount=-points_required,
                        transaction_type='spend',
                        booking=booking
                    )
                    
                else:  # payment_method == 'card'
                    # Apply loyalty discount if user has a tier
                    if user_loyalty.tier:
                        discount_percentage_decimal = Decimal(user_loyalty.tier.discount_percentage) / Decimal(100)
                        discount = total_price * discount_percentage_decimal
                        total_price -= discount

                    # Simulate payment (for now, assume success)
                    payment_success = True

                    if payment_success:
                        # Create booking with discounted price
                        booking = Booking.objects.create(
                            user=request.user,
                            session=session,
                            booked_seats=seats_to_book,
                            total_price=total_price,
                            status='confirmed'
                        )
                        
                        # Add points for the purchase (based on discounted price)
                        points_earned = int(float(total_price))
                        # Add points to current balance and total earned for tier calculation
                        user_loyalty.points += points_earned
                        user_loyalty.total_earned_points += points_earned
                        user_loyalty.save()

                        # Update user tier based on total earned points
                        user_loyalty.update_tier()

                        # Record point transaction
                        PointTransaction.objects.create(
                            user_loyalty=user_loyalty,
                            amount=points_earned,
                            transaction_type='earn',
                            booking=booking
                        )

                messages.success(request, 'Tickets booked successfully!', extra_tags='success')
                return redirect('account:user_profile_detail')
        else:
            print("No seats selected in POST request.")

    context = {
        'movie': movie,
        'available_dates': available_dates,
        'selected_date': selected_date,
        'sessions_for_date': sessions_for_date,
        'session': session, # The finally selected session
    }
    
    return render(request, 'movie/book_ticket.html', context)

def schedule_view(request):
    """Renders the schedule page showing movie sessions for a selected date."""
    selected_date_str = request.GET.get('date')
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date string, maybe redirect to today's schedule
            selected_date = today
    else:
        selected_date = today

    # Get all sessions for the selected date
    sessions = MovieSession.objects.filter(date=selected_date).order_by('movie', 'time', 'hall__name')
    
    # Group sessions by movie
    movie_sessions = {}
    for session in sessions:
        if session.movie not in movie_sessions:
            movie_sessions[session.movie] = []
        movie_sessions[session.movie].append(session)

    context = {
        'movie_sessions': movie_sessions,
        'selected_date': selected_date,
        'today': today,
        'tomorrow': tomorrow,
    }
    return render(request, 'movie/schedule.html', context)
