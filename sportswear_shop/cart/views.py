from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from typing import Optional

from .models import Cart, CartItem
from shop.models import Product
from discounts.models import Discount

@login_required
def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Отображает детали корзины с возможностью применения скидки.

    :param request: Объект запроса.
    :return: HTML-ответ с деталями корзины.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    discounts = Discount.objects.all()
    selected_discount_id: Optional[str] = request.POST.get('discount_id')
    selected_discount: Optional[Discount] = None

    if selected_discount_id:
        try:
            selected_discount = Discount.objects.get(id=selected_discount_id)
        except Discount.DoesNotExist:
            selected_discount = None

    for item in cart.items.all():
        item.total = item.product.price * item.quantity

    total_price: float = sum(item.get_total() for item in cart.items.all())

    discount_amount: float = 0
    final_price: float = total_price
    if selected_discount:
        discount_amount = total_price * selected_discount.discount_percent / 100
        final_price = total_price - discount_amount

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'discounts': discounts,
        'selected_discount_id': int(selected_discount_id) if selected_discount_id else None,
        'total_price': total_price,
        'discount_amount': discount_amount,
        'final_price': final_price,
    })

@require_POST
@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Добавляет товар в корзину пользователя.

    :param request: Объект запроса.
    :param product_id: Идентификатор добавляемого товара.
    :return: Редирект на страницу корзины.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product: Product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        item.quantity = 1
    else:
        item.quantity += 1
    item.save()
    return redirect('cart_detail')

@login_required
def remove_from_cart(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Удаляет товар из корзины пользователя.

    :param request: Объект запроса.
    :param item_id: Идентификатор удаляемого элемента корзины.
    :return: Редирект на страницу корзины.
    """
    item: CartItem = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')

@login_required
def update_cart_item(request: HttpRequest, item_id: int) -> JsonResponse:
    """
    Обновляет количество товара в корзине (увеличение/уменьшение).

    :param request: Объект запроса.
    :param item_id: Идентификатор элемента корзины.
    :return: JSON-ответ с обновлённой информацией о товаре и корзине.
    """
    if request.method == 'POST':
        item: CartItem = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action: Optional[str] = request.POST.get('action')
        if action == 'plus':
            item.quantity += 1
            item.save()
        elif action == 'minus' and item.quantity > 1:
            item.quantity -= 1
            item.save()

        item_sum: float = item.get_total()
        cart: Cart = item.cart
        total: float = sum(i.get_total() for i in cart.items.all())
        return JsonResponse({'quantity': item.quantity, 'item_sum': item_sum, 'total': total})

    return JsonResponse({'error': 'Invalid request'}, status=400)
