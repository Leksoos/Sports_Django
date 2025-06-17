from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    email_verified = models.BooleanField(default=False, verbose_name="Почта подтверждена")
    favorite_products = models.ManyToManyField(
        'shop.Product',
        related_name='favorited_by',
        blank=True,
        verbose_name="Избранные товары"
    )
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']

class UserGroup(Group):
    class Meta:
        proxy = True
        verbose_name = "Группа доступа"
        verbose_name_plural = "Группы доступа"