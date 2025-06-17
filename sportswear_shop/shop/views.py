from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg, Sum, Q
from .models import Product, Category
from .forms import ProductForm
from discounts.models import Discount
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializer
from rest_framework import generics
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from reviews.forms import ReviewForm

def index(request):
    search_query = request.GET.get('q', '')
    new_products = Product.objects.order_by('-created_at')[:5]
    popular_products = Product.objects.annotate(order_count=Count('order_items')).order_by('-order_count')[:5]
    active_discounts = Discount.objects.filter(active=True).order_by('-discount_percent')[:5]
    avg_price = Product.objects.aggregate(Avg('price'))['price__avg']
    categories = Category.objects.all()

    search_results = None
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

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ReviewForm()
    return render(request, 'shop/product_detail.html', {'product': product, 'form': form})

def discount_detail(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    return render(request, 'discounts/discount_detail.html', {'discount': discount})

def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, 'discounts/discount_list.html', {'discounts': discounts})

def product_list(request):
    # Получаем параметры поиска
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    # Базовый запрос с оптимизацией
    products = Product.objects.all().select_related('category', 'brand')
    
    # Применяем фильтры
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
    
    # Агрегация
    avg_price = products.aggregate(Avg('price'))
    total_stock = products.aggregate(Sum('stock'))
    category_counts = Product.objects.values('category__name').annotate(Count('id'))
    
    # Оптимизация ManyToMany
    products = products.prefetch_related('tags')
    
    return render(request, 'shop/product_list.html', {
        'products': products,
        'expensive_products': expensive_products,
        'available_products': available_products,
        'sorted_products': sorted_products,
        'avg_price': avg_price,
        'total_stock': total_stock,
        'category_counts': category_counts,
        'search_query': search_query,  #Передаем обратно в шаблон
    })

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'shop/product_confirm_delete.html', {'product': product})


def product_list_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'shop/product_list.html', {
        'products': products,
        'category': category,
    })

class ProductDetailAPIView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, context={'user': request.user})
        return Response(serializer.data)

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all().select_related('category', 'brand')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

@login_required
def add_review(request, pk):
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
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user or request.user.is_staff:
        review.delete()
    return redirect('product_detail', pk=review.product.pk)
