from django.db import models
from shop.models import Product
from orders.models import Order

class Discount(models.Model):
    """
    Модель скидки, применяемой к товарам.
    """
    name: str = models.CharField(max_length=100, verbose_name="Название")
    products: models.ManyToManyField = models.ManyToManyField(Product, related_name="discounts", verbose_name="Товары")
    discount_percent: int = models.PositiveIntegerField(verbose_name="Скидка в %")
    active: bool = models.BooleanField(default=True, verbose_name="Активна")
    start_date: models.DateTimeField = models.DateTimeField(verbose_name="Дата начала")
    end_date: models.DateTimeField = models.DateTimeField(verbose_name="Дата окончания")

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def __str__(self) -> str:
        """
        Возвращает строковое представление скидки.

        :return: Название и процент скидки.
        """
        return f"{self.name} - {self.discount_percent}%"

class OrderItem(models.Model):
    """
    Модель товара в заказе с учетом скидки.
    """
    order: models.ForeignKey = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="discount_items")
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар", related_name="discount_order_items")
    quantity: int = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

    def __str__(self) -> str:
        """
        Возвращает строковое представление товара в заказе.

        :return: Название товара и количество.
        """
        return f"{self.product.name} x {self.quantity}"
