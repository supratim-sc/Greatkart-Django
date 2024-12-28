from django import forms

from .models import ReviewRatings

class ReviewRatingsForm(forms.ModelForm):
    class Meta:
        model = ReviewRatings
        fields = ['subject', 'review', 'ratings']