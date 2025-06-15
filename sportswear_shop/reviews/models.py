from django.db import models
from django.conf import settings
from shop.models import Product

class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    rating = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField(
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата отзыва"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Отзыв {self.user.username} ({self.rating}★) о {self.product.name}"