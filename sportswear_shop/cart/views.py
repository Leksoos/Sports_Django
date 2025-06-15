from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from shop.models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from discounts.models import Discount 
from django.http import JsonResponse

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    discounts = Discount.objects.all()
    selected_discount_id = request.POST.get('discount_id')
    selected_discount = None
    if selected_discount_id:
        try:
            selected_discount = Discount.objects.get(id=selected_discount_id)
        except Discount.DoesNotExist:
            selected_discount = None

    # Считаем сумму по каждой позиции
    for item in cart.items.all():
        item.total = item.product.price * item.quantity

    total_price = sum(item.get_total() for item in cart.items.all())

    discount_amount = 0
    final_price = total_price
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
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        item.quantity = 1
    else:
        item.quantity += 1
    item.save()
    return redirect('cart_detail')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        if action == 'plus':
            item.quantity += 1
            item.save()
        elif action == 'minus' and item.quantity > 1:
            item.quantity -= 1
            item.save()
        item_sum = item.get_total()
        cart = item.cart
        total = sum(i.get_total() for i in cart.items.all())
        return JsonResponse({'quantity': item.quantity, 'item_sum': item_sum, 'total': total})
    return JsonResponse({'error': 'Invalid request'}, status=400)