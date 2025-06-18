from typing import Any, Optional
from rest_framework import serializers
from .models import Product, ProductImage, Category, Brand

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для изображений товара.
    """
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для товара с вложенными изображениями и полем избранного.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'category', 'brand', 'images', 'is_favorite']

    def get_is_favorite(self, obj: Product) -> bool:
        """
        Определяет, является ли товар избранным для текущего пользователя.

        Args:
            obj (Product): экземпляр продукта.

        Returns:
            bool: True, если товар в избранных пользователя, иначе False.
        """
        user: Optional[Any] = self.context.get('user')
        if user and user.is_authenticated:
            # Предполагается, что у пользователя есть related_name 'favorite_products'
            favorite_products = getattr(user, 'favorite_products', None)
            if favorite_products:
                return favorite_products.filter(pk=obj.pk).exists()
        return False
