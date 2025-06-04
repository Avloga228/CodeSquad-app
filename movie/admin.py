from django.contrib import admin
from .models import Movie, CinemaHall, MovieSession, Booking, Genre, HomepageSettings, LoyaltyTier, UserLoyalty, PointTransaction

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'rating', 'is_active', 'created_at', 'horizontal_poster')
    list_filter = ('genres', 'release_date', 'rating', 'is_active')
    search_fields = ('title', 'description', 'directors')
    filter_horizontal = ('genres',)
    date_hierarchy = 'release_date'

@admin.register(CinemaHall)
class CinemaHallAdmin(admin.ModelAdmin):
    list_display = ('name', 'rows', 'seats_per_row')
    search_fields = ('name',)

@admin.register(MovieSession)
class MovieSessionAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'date', 'time', 'price', 'get_available_seats', 'is_active')
    list_filter = ('date', 'is_active', 'hall')
    search_fields = ('movie__title', 'hall__name')
    date_hierarchy = 'date'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'total_price', 'booking_date', 'status')
    list_filter = ('status', 'booking_date', 'session__date')
    search_fields = ('user__username', 'session__movie__title')
    date_hierarchy = 'booking_date'

@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Featured Movies (Carousel)', {
            'description': 'Select up to 3 movies to display in the homepage carousel.',
            'fields': ('featured_movies',),
        }),
        ('Now Playing Section', {
            'description': 'Select up to 4 movies to display in the Now Playing section.',
            'fields': ('now_playing_movies',),
        }),
        ('Coming Soon Section', {
            'description': 'Select up to 4 movies to display in the Coming Soon section.',
            'fields': ('coming_soon_movies',),
        }),
        ('Top Rated Movies Section', {
            'description': 'Select up to 4 top rated movies to display.',
            'fields': ('top_rated_movies',),
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False

@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'discount_percentage')
    ordering = ('points_required',)
    search_fields = ('name',)

@admin.register(UserLoyalty)
class UserLoyaltyAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'tier', 'last_updated')
    list_filter = ('tier',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_updated',)
    ordering = ('-points',)

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'amount', 'transaction_type', 'created_at', 'booking')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user_loyalty__user__username', 'user_loyalty__user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_username(self, obj):
        return obj.user_loyalty.user.username
    get_username.short_description = 'User'
