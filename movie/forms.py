from django import forms
from .models import Movie

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            'title', 'genres', 'release_date', 'description', 'directors',
            'country', 'duration', 'poster', 'horizontal_poster', 'trailer_link', 'rating',
            'language', 'is_active'
        ]
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
