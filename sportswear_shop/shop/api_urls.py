from django.urls import path
from .views import ProductListAPIView, ProductDetailAPIView

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='api_product_list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
]