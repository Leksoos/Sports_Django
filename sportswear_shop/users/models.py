from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class User(AbstractUser):
    """
    Пользователь с дополнительными полями:
    - phone: телефонный номер
    - avatar: аватар пользователя
    - email_verified: флаг подтверждения почты
    - favorite_products: избранные товары пользователя (ManyToMany с моделью Product)
    """
    phone: models.CharField = models.CharField(
        max_length=20, blank=True, verbose_name="Телефон"
    )
    avatar: models.ImageField = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name="Аватар"
    )
    email_verified: models.BooleanField = models.BooleanField(
        default=False, verbose_name="Почта подтверждена"
    )
    favorite_products: models.ManyToManyField = models.ManyToManyField(
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
    """
    Прокси-модель для Group с кастомными мета-опциями
    (для кастомизации админки и отображения).
    """
    class Meta:
        proxy = True
        verbose_name = "Группа доступа"
        verbose_name_plural = "Группы доступа"
