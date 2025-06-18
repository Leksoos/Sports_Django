from typing import Any
from django.db import models
from orders.models import Order
import uuid

class Payment(models.Model):
    """
    Модель для хранения информации о платежах.
    """
    PAYMENT_METHODS = [
        ('card', 'Карта'),
        ('paypal', 'PayPal'),
        ('cash', 'Наличные'),
    ]

    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('completed', 'Завершен'),
        ('failed', 'Неудачный'),
    ]

    order: models.ForeignKey = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Заказ"
    )
    payment_method: models.CharField = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты"
    )
    status: models.CharField = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    transaction_id: models.CharField = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID транзакции"
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата платежа"
    )

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self) -> str:
        """
        Возвращает строковое представление объекта оплаты.
        """
        return f"Оплата {self.transaction_id} - {self.status}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределённый метод save, который генерирует уникальный transaction_id,
        если он не задан.
        """
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
