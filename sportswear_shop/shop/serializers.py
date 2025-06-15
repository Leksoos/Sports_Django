from rest_framework import serializers
from .models import Product, ProductImage, Category, Brand

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'category', 'brand', 'images', 'is_favorite']

    def get_is_favorite(self, obj):
        user = self.context.get('user')
        # если у пользователя есть избранные товары
        if user and user.is_authenticated:
            return obj in getattr(user, 'favorite_products', []).all()
        return False