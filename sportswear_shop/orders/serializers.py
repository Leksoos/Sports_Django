from typing import Any
from rest_framework import serializers
from .models import Order, OrderItem
from shop.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения одного товара в заказе.
    """
    product = ProductSerializer(read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_cost']

    def get_total_cost(self, obj: OrderItem) -> float:
        """
        Возвращает общую стоимость товара в заказе.

        :param obj: объект OrderItem
        :return: стоимость (цена * количество)
        """
        return obj.total_cost


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения заказа.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'discounted_total', 'created_at', 'items', 'can_cancel']

    def get_can_cancel(self, obj: Order) -> bool:
        """
        Проверяет, может ли текущий пользователь отменить заказ.

        :param obj: объект Order
        :return: True, если можно отменить заказ, иначе False
        """
        user: Any = self.context.get('user')
        return bool(user and obj.user == user and obj.status == 'pending')
