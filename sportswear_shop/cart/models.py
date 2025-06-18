from django.db import models
from django.conf import settings
from shop.models import Product

class Cart(models.Model):
    """Модель корзины, связанная с пользователем."""
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts'
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    """Элемент корзины, содержащий товар и его количество."""
    cart: models.ForeignKey = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(default=1)

    def get_total(self) -> float:
        """
        Возвращает общую стоимость данного товара в корзине.

        :return: Общая стоимость товара (цена * количество).
        """
        return self.product.price * self.quantity
