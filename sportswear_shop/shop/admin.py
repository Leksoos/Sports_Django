from django.contrib import admin
from .models import Category, Brand, Product, ProductImage
from django.utils.html import format_html

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_count')
    search_fields = ('name',)
    
    @admin.display(description='Товаров')
    def product_count(self, obj):
        return obj.products.count()

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_count')
    search_fields = ('name',)
    
    @admin.display(description='Товаров')
    def product_count(self, obj):
        return obj.products.count()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price_display', 'brand', 'category', 'stock', 'stock_status', 'created_at')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'brand__name', 'category__name')
    raw_id_fields = ('brand', 'category')
    readonly_fields = ('created_at',)
    inlines = [ProductImageInline]

    @admin.display(description='Цена')
    def price_display(self, obj):
        return f'{obj.price:.2f} ₽'

    @admin.display(description='Наличие')
    def stock_status(self, obj):
        if obj.stock > 10:
            return '✓ В наличии'
        return f'{obj.stock} шт' if obj.stock > 0 else '✗ Нет'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'uploaded_at')

    @admin.display(description='Превью')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 60px;" />', obj.image.url)
        return "—"
