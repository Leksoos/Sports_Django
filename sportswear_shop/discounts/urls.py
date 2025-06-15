from django.urls import path
from .views import discount_list, discount_detail

urlpatterns = [
    path('', discount_list, name='discount_list'),
    path('<int:pk>/', discount_detail, name='discount_detail'),
]