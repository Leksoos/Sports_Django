from typing import Any
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductManager(models.Manager):
    def available(self) -> models.QuerySet["Product"]:
        """
        Возвращает queryset товаров с количеством на складе больше 0.
        """
        return self.filter(stock__gt=0)

class Category(models.Model):
    """
    Категория товаров.
    """
    name: models.CharField = models.CharField(max_length=100, unique=True, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name

class Brand(models.Model):
    """
    Бренд товаров.
    """
    name: models.CharField = models.CharField(max_length=100, unique=True, verbose_name="Название бренда")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    """
    Товар с основными характеристиками.
    """
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    name: models.CharField = models.CharField(max_length=255, verbose_name="Название")
    description: models.TextField = models.TextField(verbose_name="Описание")
    price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name="Количество на складе")
    category: models.ForeignKey = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    brand: models.ForeignKey = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', verbose_name="Бренд")
    created_at: models.DateTimeField = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    size: models.CharField = models.CharField(max_length=2, choices=SIZE_CHOICES, verbose_name="Размер")

    tags: models.ManyToManyField = models.ManyToManyField("Tag", through="ProductTag", verbose_name="Теги")
    objects: ProductManager = ProductManager()

    external_page: models.URLField = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на страницу производителя"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def get_absolute_url(self) -> str:
        """
        Возвращает URL детальной страницы товара.
        """
        return reverse('product_detail', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return self.name

class Tag(models.Model):
    """
    Тег для маркировки товаров.
    """
    name: models.CharField = models.CharField(max_length=100, unique=True, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.name

class ProductTag(models.Model):
    """
    Промежуточная модель связи товара и тега.
    """
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    tag: models.ForeignKey = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")
    added_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Тег товара"
        verbose_name_plural = "Теги товаров"

    def __str__(self) -> str:
        return f"{self.product.name} - {self.tag.name}"

class ProductImage(models.Model):
    """
    Изображение товара.
    """
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image: models.ImageField = models.ImageField(upload_to='products/', verbose_name="Изображение")
    uploaded_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self) -> str:
        return f"Изображение для {self.product.name}"

class apexam(models.Model):
    """
    Модель для хранения информации о экзаменах и пользователях, которые их пишут.
    """
    name = models.CharField("Название экзамена", max_length=255)
    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)
    exam_date = models.DateField("Дата проведения экзамена")
    image = models.ImageField("Задание (картинка)", upload_to='exam_images/')
    users = models.ManyToManyField(User, verbose_name="Пользователи")
    is_public = models.BooleanField("Опубликовано", default=False)

    def __str__(self) -> str:
        return self.name
