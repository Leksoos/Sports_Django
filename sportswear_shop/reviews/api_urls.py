from django.urls import path
from .api_views import ReviewListCreateAPIView, ReviewRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('reviews/', ReviewListCreateAPIView.as_view(), name='api_review_list_create'),
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyAPIView.as_view(), name='api_review_detail'),
]