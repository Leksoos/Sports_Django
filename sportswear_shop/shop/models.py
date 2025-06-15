from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

class ProductManager(models.Manager):
    def available(self):
        return self.filter(stock__gt=0)

# Категории товаров
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

# Бренды товаров
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название бренда")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name

# Товар
class Product(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(verbose_name="Количество на складе")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', verbose_name="Бренд")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, verbose_name="Размер")

    tags = models.ManyToManyField("Tag", through="ProductTag", verbose_name="Теги")
    objects = ProductManager()

    external_page = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на страницу производителя"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

# Теги товаров
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name

# Связь товаров и тегов
class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Тег товара"
        verbose_name_plural = "Теги товаров"

    def __str__(self):
        return f"{self.product.name} - {self.tag.name}"

# Изображения для товаров
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Изображение для {self.product.name}"

# Комментарии к товарам
class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # 1-5 звёзд
    created_at = models.DateTimeField(auto_now_add=True)
