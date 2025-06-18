from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    """
    Форма для создания и редактирования отзывов.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '★' * i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }