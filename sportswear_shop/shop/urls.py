from django.urls import path
from .views import product_list, product_create, product_update, product_delete, product_detail, discount_detail, discount_list
from .views import ProductDetailAPIView, ProductListAPIView
from reviews.views import add_review, delete_review, edit_review
from . import views

urlpatterns = [
    path('', product_list, name='product_list'),  # Каталог товаров
    path('discounts/', discount_list, name='discount_list'),  # Список акций
    path('product/add/', product_create, name='product_create'),
    path('product/<int:pk>/edit/', product_update, name='product_update'),
    path('product/<int:pk>/delete/', product_delete, name='product_delete'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('<int:pk>/', discount_detail, name='discount_detail'),
    path('category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('products/', ProductListAPIView.as_view(), name='api_product_list'),
    path('product/<int:pk>/add_review/', add_review, name='add_review'),
    path('review/<int:review_id>/delete/', delete_review, name='delete_review'),
    path('review/<int:review_id>/edit/', edit_review, name='edit_review'),
]
