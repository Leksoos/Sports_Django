from typing import Optional
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg, Sum, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category
from .forms import ProductForm
from discounts.models import Discount
from reviews.forms import ReviewForm
from .serializers import ProductSerializer
from .filters import ProductFilter
from reviews.models import Review


def index(request: HttpRequest) -> HttpResponse:
    """
    Главная страница с подборками товаров и активными скидками.

    Args:
        request (HttpRequest): HTTP-запрос.

    Returns:
        HttpResponse: Отрендеренная главная страница.
    """
    search_query: str = request.GET.get('q', '')
    new_products: QuerySet = Product.objects.order_by('-created_at')[:5]
    popular_products: QuerySet = Product.objects.annotate(order_count=Count('order_items')).order_by('-order_count')[:5]
    active_discounts: QuerySet = Discount.objects.filter(active=True).order_by('-discount_percent')[:5]
    avg_price: Optional[float] = Product.objects.aggregate(Avg('price'))['price__avg']
    categories: QuerySet = Category.objects.all()

    search_results: Optional[QuerySet] = None
    if search_query:
        search_results = Product.objects.filter(name__icontains=search_query)

    return render(request, 'shop/index.html', {
        'new_products': new_products,
        'popular_products': popular_products,
        'active_discounts': active_discounts,
        'avg_price': avg_price,
        'search_query': search_query,
        'search_results': search_results,
        'categories': categories,
    })


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Детальная страница товара.

    Args:
        request (HttpRequest): HTTP-запрос.
        pk (int): ID товара.

    Returns:
        HttpResponse: Отрендеренная страница товара.
    """
    product: Product = get_object_or_404(Product, pk=pk)
    form: ReviewForm = ReviewForm()
    return render(request, 'shop/product_detail.html', {'product': product, 'form': form})


def discount_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Детальная страница скидки.

    Args:
        request (HttpRequest): HTTP-запрос.
        pk (int): ID скидки.

    Returns:
        HttpResponse: Отрендеренная страница скидки.
    """
    discount = get_object_or_404(Discount, pk=pk)
    return render(request, 'discounts/discount_detail.html', {'discount': discount})


def discount_list(request: HttpRequest) -> HttpResponse:
    """
    Список всех скидок.

    Args:
        request (HttpRequest): HTTP-запрос.

    Returns:
        HttpResponse: Отрендеренная страница со скидками.
    """
    discounts = Discount.objects.all()
    return render(request, 'discounts/discount_list.html', {'discounts': discounts})


def product_list(request: HttpRequest) -> HttpResponse:
    """
    Список товаров с фильтрацией и поиском.

    Args:
        request (HttpRequest): HTTP-запрос.

    Returns:
        HttpResponse: Отрендеренная страница со списком товаров.
    """
    search_query: str = request.GET.get('search', '')
    category_filter: str = request.GET.get('category', '')

    products: QuerySet = Product.objects.all().select_related('category', 'brand')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category__name__icontains=category_filter)

    expensive_products = products.filter(price__gt=5000)
    available_products = products.exclude(stock=0)
    sorted_products = products.order_by('-price')

    avg_price = products.aggregate(Avg('price'))
    total_stock = products.aggregate(Sum('stock'))
    category_counts = Product.objects.values('category__name').annotate(Count('id'))

    products = products.prefetch_related('tags')

    return render(request, 'shop/product_list.html', {
        'products': products,
        'expensive_products': expensive_products,
        'available_products': available_products,
        'sorted_products': sorted_products,
        'avg_price': avg_price,
        'total_stock': total_stock,
        'category_counts': category_counts,
        'search_query': search_query,
    })


def product_create(request: HttpRequest) -> HttpResponse:
    """
    Создание нового товара.

    Args:
        request (HttpRequest): HTTP-запрос.

    Returns:
        HttpResponse: Рендер формы создания или редирект после успешного сохранения.
    """
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form})


def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Обновление существующего товара.

    Args:
        request (HttpRequest): HTTP-запрос.
        pk (int): ID товара.

    Returns:
        HttpResponse: Рендер формы редактирования или редирект после сохранения.
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form})


def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаление товара.

    Args:
        request (HttpRequest): HTTP-запрос.
        pk (int): ID товара.

    Returns:
        HttpResponse: Рендер страницы подтверждения удаления или редирект после удаления.
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'shop/product_confirm_delete.html', {'product': product})


def product_list_by_category(request: HttpRequest, category_id: int) -> HttpResponse:
    """
    Список товаров по категории.

    Args:
        request (HttpRequest): HTTP-запрос.
        category_id (int): ID категории.

    Returns:
        HttpResponse: Отрендеренная страница со списком товаров.
    """
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/product_list.html', {
        'products': products,
        'category': category,
    })


class ProductDetailAPIView(APIView):
    """
    API для детальной информации о товаре.
    """
    def get(self, request: HttpRequest, pk: int) -> Response:
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, context={'user': request.user})
        return Response(serializer.data)


class ProductListAPIView(generics.ListAPIView):
    """
    API для списка товаров с фильтрацией.
    """
    queryset = Product.objects.all().select_related('category', 'brand')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


@login_required
def add_review(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Добавление отзыва к товару.

    Args:
        request (HttpRequest): HTTP-запрос.
        pk (int): ID товара.

    Returns:
        HttpResponse: Рендер формы или редирект после успешного добавления.
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'reviews/add_review.html', {'form': form, 'product': product})


@login_required
def delete_review(request: HttpRequest, review_id: int) -> HttpResponse:
    """
    Удаление отзыва.

    Args:
        request (HttpRequest): HTTP-запрос.
        review_id (int): ID отзыва.

    Returns:
        HttpResponse: Редирект на страницу товара.
    """
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user or request.user.is_staff:
        review.delete()
    return redirect('product_detail', pk=review.product.pk)
