from typing import Any
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from .models import Order
from .serializers import OrderSerializer


class OrderListView(generics.ListAPIView):
    """
    Представление для получения списка заказов текущего пользователя.
    Доступно только для аутентифицированных пользователей.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        """
        Возвращает QuerySet с заказами, принадлежащими текущему пользователю.

        :return: QuerySet с заказами пользователя
        """
        return Order.objects.filter(user=self.request.user)

    def get_serializer_context(self) -> dict[str, Any]:
        """
        Добавляет текущего пользователя в контекст сериализатора.

        :return: Словарь контекста
        """
        context: dict[str, Any] = super().get_serializer_context()
        context['user'] = self.request.user
        return context
