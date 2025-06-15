from django.shortcuts import render, get_object_or_404
from .models import Discount

def discount_detail(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    products = discount.products.all()
    return render(request, 'discounts/discount_detail.html', {
        'discount': discount,
        'products': products,
    })

def discount_list(request):
    discounts = Discount.objects.all()
    return render(request, 'discounts/discount_list.html', {'discounts': discounts})