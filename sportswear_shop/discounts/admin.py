from django.contrib import admin
from django.utils import timezone
from .models import Discount

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "discount_percent", "status", "duration_days", "product_count", "active_products")
    list_filter = (
        "active",
        ("start_date", admin.DateFieldListFilter),
        ("discount_percent", admin.ChoicesFieldListFilter),
    )
    filter_horizontal = ("products",)
    date_hierarchy = "start_date"
    readonly_fields = ("created_at",) if hasattr(Discount, 'created_at') else ()
    search_fields = ("name", "products__name")

    @admin.display(description="Статус скидки", ordering="start_date")
    def status(self, obj):
        now = timezone.now()
        if obj.start_date > now:
            return "Запланирована"
        elif obj.end_date < now:
            return "Завершена"
        return "Активна"

    @admin.display(description="Длительность (дни)")
    def duration_days(self, obj):
        return (obj.end_date - obj.start_date).days

    @admin.display(description="Товаров со скидкой")
    def product_count(self, obj):
        return obj.products.count()

    @admin.display(description="Доступных товаров")
    def active_products(self, obj):
        # Фильтруем по полю stock (количество на складе)
        return obj.products.filter(stock__gt=0).count()
