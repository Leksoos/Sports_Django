from typing import Any
from django.db import models
from django.conf import settings
from shop.models import Product

class Review(models.Model):
    """
    Модель отзыва пользователя о товаре.

    Атрибуты:
        product (ForeignKey): Товар, к которому относится отзыв.
        user (ForeignKey): Пользователь, оставивший отзыв.
        rating (PositiveSmallIntegerField): Оценка товара (от 1 до 5).
        comment (TextField): Текст комментария.
        created_at (DateTimeField): Дата и время создания отзыва.
    """
    product: models.ForeignKey = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар"
    )
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    rating: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment: models.TextField = models.TextField(
        verbose_name="Комментарий"
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата отзыва"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self) -> str:
        """
        Возвращает строковое представление отзыва.

        :return: Строка с информацией о пользователе, рейтинге и товаре.
        """
        return f"Отзыв {self.user.username} ({self.rating}★) о {self.product.name}"
