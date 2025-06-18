import django_filters
from django.db.models.query import QuerySet
from .models import Product

class ProductFilter(django_filters.FilterSet):
    """
    Фильтр для модели Product с поддержкой фильтрации по цене, категории, бренду и наличию на складе.
    """
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr='icontains')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'price_min', 'price_max', 'in_stock']

    def filter_in_stock(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтр по наличию товара на складе.
        
        Args:
            queryset (QuerySet): исходный набор данных
            name (str): имя фильтра (unused)
            value (bool): если True, фильтрует только товары с наличием (>0)
        
        Returns:
            QuerySet: отфильтрованный набор данных
        """
        if value:
            return queryset.exclude(stock=0)
        return queryset
