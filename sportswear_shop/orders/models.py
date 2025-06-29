from typing import Optional
from django.db import models
from django.conf import settings
from shop.models import Product


class Order(models.Model):
    """
    Модель для представления заказа, сделанного пользователем.
    """

    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
    ]

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Покупатель",
        related_name="orders"
    )
    status: models.CharField = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    discounted_total: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Итого со скидкой"
    )
    total_price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Общая сумма",
        default=0
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата заказа"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    invoice: models.FileField = models.FileField(
        upload_to='orders/invoices/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Счёт-фактура",
        help_text="Загрузите PDF или изображение счёта"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        """
        Возвращает строковое представление заказа.
        """
        return f"Заказ {self.id} - {self.user.username}"


class OrderItem(models.Model):
    """
    Модель для представления отдельного товара в заказе.
    """

    order: models.ForeignKey = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product: models.ForeignKey = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
        related_name="order_items"
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество"
    )
    discount: models.ForeignKey = models.ForeignKey(
        'discounts.Discount',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Скидка"
    )
    price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        default=0
    )

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

    @property
    def total_cost(self) -> float:
        """
        Возвращает общую стоимость позиции заказа (цена * количество).
        """
        return self.quantity * (self.price or 0)

    def __str__(self) -> str:
        """
        Возвращает строковое представление позиции заказа.
        """
        return f"{self.product.name} x {self.quantity}"
