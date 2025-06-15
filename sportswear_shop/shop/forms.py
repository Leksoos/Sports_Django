from django import forms
from .models import Product, ProductComment

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'brand', 'size']

class ProductCommentForm(forms.ModelForm):
    RATING_CHOICES = [(i, '★' * i) for i in range(1, 6)]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect, label='Оценка')

    class Meta:
        model = ProductComment
        fields = ['text', 'rating']
