from rest_framework import serializers
from .models import Order, OrderItem
from shop.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_cost']

    def get_total_cost(self, obj):
        return obj.total_cost

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'discounted_total', 'created_at', 'items', 'can_cancel']

    def get_can_cancel(self, obj):
        user = self.context.get('user')
        # Пример: только владелец заказа может отменить, если статус pending
        return user and obj.user == user and obj.status == 'pending'