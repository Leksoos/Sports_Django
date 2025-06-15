from django.db import models
from shop.models import Product
from orders.models import Order

class Discount(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    products = models.ManyToManyField(Product, related_name="discounts", verbose_name="Товары")
    discount_percent = models.PositiveIntegerField(verbose_name="Скидка в %")
    active = models.BooleanField(default=True, verbose_name="Активна")
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def __str__(self):
        return f"{self.name} - {self.discount_percent}%"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="discount_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар", related_name="discount_order_items")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"