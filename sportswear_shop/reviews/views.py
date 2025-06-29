from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from shop.models import Product
from .models import Review
from .forms import ReviewForm

def product_list(request: HttpRequest) -> HttpResponse:
    """
    Выводит список товаров с фильтрацией и поиском.

    Args:
        request (HttpRequest): HTTP-запрос пользователя.

    Returns:
        HttpResponse: HTML-страница со списком товаров.
    """
    # Тело функции отсутствует в исходном коде, оставлено без изменений
    pass


@login_required
def add_review(request: HttpRequest, pk: int) -> HttpResponse | JsonResponse:
    """
    Добавляет отзыв к товару.

    Args:
        request (HttpRequest): HTTP-запрос пользователя.
        pk (int): Первичный ключ товара.

    Returns:
        HttpResponse | JsonResponse: Перенаправление или JSON-ответ с результатом.
    """
    product = get_object_or_404(Product, pk=pk)
    if Review.objects.filter(product=product, user=request.user).exists():
        return JsonResponse({'success': False, 'errors': {'__all__': ['Вы уже оставили отзыв для этого товара.']}}, status=400)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                review_html = render_to_string('shop/review_item.html', {'review': review, 'user': request.user})
                return JsonResponse({'success': True, 'review_html': review_html})
            return redirect('product_detail', pk=pk)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ReviewForm()
    return render(request, 'shop/product_detail.html', {'form': form, 'product': product})


@login_required
def delete_review(request: HttpRequest, review_id: int) -> HttpResponse:
    """
    Удаляет отзыв.

    Args:
        request (HttpRequest): HTTP-запрос пользователя.
        review_id (int): Идентификатор отзыва.

    Returns:
        HttpResponse: Перенаправление на страницу товара.
    """
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user or request.user.is_staff:
        review.delete()
    return redirect('product_detail', pk=review.product.pk)


@login_required
def edit_review(request: HttpRequest, review_id: int) -> HttpResponse:
    """
    Редактирует существующий отзыв.

    Args:
        request (HttpRequest): HTTP-запрос пользователя.
        review_id (int): Идентификатор отзыва.

    Returns:
        HttpResponse: Страница с формой редактирования или перенаправление после успешного сохранения.
    """
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user and not request.user.is_staff:
        return redirect('product_detail', pk=review.product.pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=review.product.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form, 'review': review})
