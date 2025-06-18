from typing import Any
from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Review.
    Отображает основные поля в списке, позволяет фильтровать и искать отзывы.
    """
    list_display = ('id', 'product', 'user', 'rating_stars', 'short_comment', 'created_at')
    list_filter = ('rating', 'created_at', 'product')
    search_fields = ('product__name', 'user__username', 'comment')
    raw_id_fields = ('product', 'user')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    @admin.display(description='Оценка')
    def rating_stars(self, obj: Review) -> str:
        """
        Возвращает строку с рейтингом в виде звёздочек (★) и пустых звёзд (☆).
        """
        return '★' * obj.rating + '☆' * (5 - obj.rating)

    @admin.display(description='Комментарий')
    def short_comment(self, obj: Review) -> str:
        """
        Возвращает укороченный комментарий (до 50 символов) с добавлением троеточия,
        если комментарий длиннее 50 символов.
        """
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
