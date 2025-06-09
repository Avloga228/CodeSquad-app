"""
Management command to populate the database with sample data for testing.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from movie.models import (
    Genre, Movie, CinemaHall, MovieSession, Booking,
    LoyaltyTier, UserLoyalty, PointTransaction, HomepageSettings
)
from review.models import Review
from user_profile.models import UserProfile

class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        
        try:
            with transaction.atomic():
                self.stdout.write('Starting to populate sample data...')
                
                # Create sample data
                self.create_genres()
                self.create_movies()
                self.create_cinema_halls()
                self.create_movie_sessions()
                self.create_users()
                self.create_reviews()
                self.create_bookings()
                self.create_loyalty_data()
                
                self.stdout.write(self.style.SUCCESS('Successfully populated sample data!'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error populating sample data: {str(e)}')
            )
            raise

    def clear_data(self):
        """Clear all existing data from the database."""
        self.stdout.write('Clearing existing data...')
        
        # Delete in reverse order of dependencies
        PointTransaction.objects.all().delete()
        UserLoyalty.objects.all().delete()
        Booking.objects.all().delete()
        MovieSession.objects.all().delete()
        Review.objects.all().delete()
        UserProfile.objects.all().delete()
        Movie.objects.all().delete()
        Genre.objects.all().delete()
        CinemaHall.objects.all().delete()
        HomepageSettings.objects.all().delete()
        
        # Don't delete superusers
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write('Existing data cleared.')

    def create_genres(self):
        """Create sample genres."""
        self.stdout.write('Creating genres...')
        
        genres_data = [
            {'name': 'Бойовик', 'slug': 'action'},
            {'name': 'Комедія', 'slug': 'comedy'},
            {'name': 'Драма', 'slug': 'drama'},
            {'name': 'Фантастика', 'slug': 'science-fiction'},
            {'name': 'Жахи', 'slug': 'horror'},
            {'name': 'Романтика', 'slug': 'romance'},
            {'name': 'Трилер', 'slug': 'thriller'},
            {'name': 'Пригоди', 'slug': 'adventure'},
            {'name': 'Фентезі', 'slug': 'fantasy'},
            {'name': 'Кримінал', 'slug': 'crime'},
            {'name': 'Детектив', 'slug': 'mystery'},
            {'name': 'Анімація', 'slug': 'animation'},
            {'name': 'Документальний', 'slug': 'documentary'},
            {'name': 'Сімейний', 'slug': 'family'},
            {'name': 'Історичний', 'slug': 'historical'},
            {'name': 'Мелодрама', 'slug': 'melodrama'},
            {'name': 'Музичний', 'slug': 'musical'},
            {'name': 'Військовий', 'slug': 'war'},
            {'name': 'Вестерн', 'slug': 'western'},
            {'name': 'Біографічний', 'slug': 'biography'},
        ]
        
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(
                slug=genre_data['slug'],
                defaults={'name': genre_data['name']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created genre: {genre.name} ({genre.slug})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Genre {genre.name} ({genre.slug}) already exists'
                    )
                )

    def create_movies(self):
        """Create sample movies."""
        self.stdout.write('Creating movies...')
        
        import os
        from django.core.files import File
        from datetime import date
        
        movies_data = [
            {
                'slug': 'deadpool',
                'title': 'Дедпул',
                'genres': ['action', 'comedy', 'adventure'],
                'release_date': date(2016, 2, 12),
                'description': 'Колишній спецназівець Уейд Вілсон стає найманим вбивцею. Після експериментального лікування від раку, він отримує надлюдські здібності до регенерації, але за це платить страшною деформацією обличчя. Тепер він намагається знайти людину, яка зробила його таким, і стає Дедпулом - безсоромним, саркастичним супергероєм.',
                'directors': 'Тім Міллер',
                'country': 'США',
                'duration': 108,
                'poster': 'sampledata/deadpool.jpg',
                'horizontal_poster': 'sampledata/deadpool_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=ONHBaC-pfsk',
                'rating': 8.0,
                'language': 'Англійська',
            },
            {
                'slug': 'avengers-endgame',
                'title': 'Месники: Завершення',
                'genres': ['action', 'science-fiction', 'adventure'],
                'release_date': date(2019, 4, 26),
                'description': 'Після руйнівних подій "Війни нескінченності" всесвіт залишився в руїнах. Завдяки залишкам Месників та їх союзників, вони намагаються зібрати всіх для того, щоб скасувати дії Таноса та відновити баланс у всесвіті.',
                'directors': 'Ентоні Руссо, Джо Руссо',
                'country': 'США',
                'duration': 181,
                'poster': 'sampledata/avengers.jpg',
                'horizontal_poster': 'sampledata/avengers_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=TcMBFSGVi1c',
                'rating': 8.4,
                'language': 'Англійська',
            },
            {
                'slug': 'black-panther',
                'title': 'Чорна Пантера',
                'genres': ['action', 'adventure', 'science-fiction'],
                'release_date': date(2018, 2, 16),
                'description': 'Після смерті свого батька, Т\'Чалла повертається додому в ізольовану африканську націю Ваканда, щоб зайняти трон. Однак, коли старий ворог знову з\'являється, Т\'Чалла повинен захистити свій народ від загрози, яка може знищити Ваканду.',
                'directors': 'Раян Куглер',
                'country': 'США',
                'duration': 134,
                'poster': 'sampledata/blackpanther.jpg',
                'horizontal_poster': 'sampledata/blackpanther_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=xjDjIWPwcPU',
                'rating': 7.3,
                'language': 'Англійська',
            },
            {
                'slug': 'the-drop',
                'title': 'Крапля',
                'genres': ['drama', 'thriller', 'mystery'],
                'release_date': date(2025, 3, 15),
                'description': 'Молода пара випадково знаходить дитину в сміттєвому баку. Їхнє рішення врятувати дитину призводить до несподіваних наслідків, які змінюють їхнє життя назавжди. Фільм про моральний вибір, відповідальність та силу родинних зв\'язків.',
                'directors': 'Сара Адріна Сміт',
                'country': 'США',
                'duration': 106,
                'poster': 'sampledata/drop.jpg',
                'horizontal_poster': 'sampledata/drop_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=uD4izuDMUQA',
                'rating': 7.8,
                'language': 'Англійська',
            },
            {
                'slug': 'mission-impossible-dead-reckoning',
                'title': 'Місія нездійсненна: Розплата',
                'genres': ['action', 'adventure', 'thriller'],
                'release_date': date(2023, 7, 12),
                'description': 'Ітан Хант і його команда МНЗ повертаються в новій частині франшизи. На цей раз вони зіткнуться з найнебезпечнішим ворогом, який загрожує всьому світу.',
                'directors': 'Крістофер МакКворрі',
                'country': 'США',
                'duration': 163,
                'poster': 'sampledata/missionimpossible.jpg',
                'horizontal_poster': 'sampledata/missionimpossible_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=avz06PDqDbM',
                'rating': 7.7,
                'language': 'Англійська',
            },
            {
                'slug': 'knockout',
                'title': 'Нокаут',
                'genres': ['action', 'drama', 'thriller'],
                'release_date': date(2024, 4, 5),
                'description': 'Історія про колишнього боксера, який намагається повернутися в спорт після важкої травми. Фільм про перемогу над собою, дружбу та незламність духу.',
                'directors': 'Джон Сміт',
                'country': 'США',
                'duration': 118,
                'poster': 'sampledata/knockout.jpg',
                'horizontal_poster': 'sampledata/knockout_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=uD4izuDMUQA',
                'rating': 7.5,
                'language': 'Англійська',
            },
            {
                'slug': 'minecraft',
                'title': 'Майнкрафт',
                'genres': ['adventure', 'family', 'fantasy'],
                'release_date': date(2025, 4, 4),
                'description': 'Екранізація популярної відеогри Minecraft. Молода дівчина намагається врятувати свій блоковий світ від знищення, зустрічаючи на своєму шляху різних персонажів з гри.',
                'directors': 'Джаред Хесс',
                'country': 'США',
                'duration': 110,
                'poster': 'sampledata/minecraft.jpg',
                'horizontal_poster': 'sampledata/minecraft_h.jpg',
                'trailer_link': 'https://www.youtube.com/watch?v=uD4izuDMUQA',
                'rating': 8.0,
                'language': 'Англійська',
            },
        ]
        
        for movie_data in movies_data:
            # Get or create the movie
            movie, created = Movie.objects.get_or_create(
                slug=movie_data['slug'],
                defaults={
                    'title': movie_data['title'],
                    'release_date': movie_data['release_date'],
                    'description': movie_data['description'],
                    'directors': movie_data['directors'],
                    'country': movie_data['country'],
                    'duration': movie_data['duration'],
                    'trailer_link': movie_data['trailer_link'],
                    'rating': movie_data['rating'],
                    'language': movie_data['language'],
                }
            )
            
            if created:
                # Add genres
                for genre_slug in movie_data['genres']:
                    genre = Genre.objects.get(slug=genre_slug)
                    movie.genres.add(genre)
                
                # Add posters
                if os.path.exists(movie_data['poster']):
                    with open(movie_data['poster'], 'rb') as f:
                        movie.poster.save(
                            os.path.basename(movie_data['poster']),
                            File(f),
                            save=True
                        )
                
                if os.path.exists(movie_data['horizontal_poster']):
                    with open(movie_data['horizontal_poster'], 'rb') as f:
                        movie.horizontal_poster.save(
                            os.path.basename(movie_data['horizontal_poster']),
                            File(f),
                            save=True
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created movie: {movie.title} ({movie.slug})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Movie {movie.title} ({movie.slug}) already exists'
                    )
                )

    def create_cinema_halls(self):
        """Create sample cinema halls."""
        self.stdout.write('Creating cinema halls...')
        
        halls_data = [
            {'name': 'Hall1', 'rows': 5, 'seats_per_row': 10},
            {'name': 'Hall2', 'rows': 7, 'seats_per_row': 7},
            {'name': 'Hall3', 'rows': 10, 'seats_per_row': 10},
        ]
        
        for hall_data in halls_data:
            hall, created = CinemaHall.objects.get_or_create(
                name=hall_data['name'],
                defaults={
                    'rows': hall_data['rows'],
                    'seats_per_row': hall_data['seats_per_row']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created hall: {hall.name} with {hall.rows} rows and {hall.seats_per_row} seats per row'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Hall {hall.name} already exists'
                    )
                )

    def create_movie_sessions(self):
        """Create sample movie sessions."""
        self.stdout.write('Creating movie sessions...')
        
        from datetime import datetime, timedelta
        import random
        
        # Get all movies and halls
        movies = Movie.objects.all()
        halls = CinemaHall.objects.all()
        
        # Define time slots
        time_slots = [
            '10:00', '12:30', '15:00', '17:30', '20:00', '22:30'
        ]
        
        # Define base prices for different times
        price_ranges = {
            '10:00': (120, 150),  # Morning shows - cheaper
            '12:30': (150, 180),  # Early afternoon
            '15:00': (180, 200),  # Afternoon
            '17:30': (200, 220),  # Early evening
            '20:00': (220, 250),  # Prime time
            '22:30': (180, 200),  # Late night
        }
        
        # Generate sessions for the next 7 days
        start_date = datetime.now().date() + timedelta(days=1)  # Start from tomorrow
        sessions_created = 0
        
        for day in range(7):  # 7 days
            current_date = start_date + timedelta(days=day)
            
            # For each day, create sessions for each movie
            for movie in movies:
                # Randomly select 2-3 time slots for each movie per day
                selected_times = random.sample(time_slots, random.randint(2, 3))
                
                for time_slot in selected_times:
                    # Randomly select a hall
                    hall = random.choice(halls)
                    
                    # Calculate price based on time slot
                    min_price, max_price = price_ranges[time_slot]
                    price = random.randint(min_price, max_price)
                    
                    # Create the session
                    session, created = MovieSession.objects.get_or_create(
                        movie=movie,
                        hall=hall,
                        date=current_date,
                        time=datetime.strptime(time_slot, '%H:%M').time(),
                        defaults={
                            'price': price,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        sessions_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created session: {movie.title} in {hall.name} on {current_date} at {time_slot} for {price} UAH'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Session already exists: {movie.title} in {hall.name} on {current_date} at {time_slot}'
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {sessions_created} movie sessions'
            )
        )

    def create_users(self):
        """Create sample users."""
        self.stdout.write('Creating users...')
        # Will be implemented
        pass

    def create_reviews(self):
        """Create sample reviews."""
        self.stdout.write('Creating reviews...')
        # Will be implemented
        pass

    def create_bookings(self):
        """Create sample bookings."""
        self.stdout.write('Creating bookings...')
        # Will be implemented
        pass

    def create_loyalty_data(self):
        """Create sample loyalty data."""
        self.stdout.write('Creating loyalty data...')
        # Will be implemented
        pass 