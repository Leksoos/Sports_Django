from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Discount

def discount_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Отображает детали конкретной скидки и связанные с ней товары.

    :param request: Объект запроса.
    :param pk: Идентификатор скидки.
    :return: HTML-страница со скидкой и её товарами.
    """
    discount: Discount = get_object_or_404(Discount, pk=pk)
    products = discount.products.all()
    return render(request, 'discounts/discount_detail.html', {
        'discount': discount,
        'products': products,
    })

def discount_list(request: HttpRequest) -> HttpResponse:
    """
    Отображает список всех доступных скидок.

    :param request: Объект запроса.
    :return: HTML-страница со списком скидок.
    """
    discounts = Discount.objects.all()
    return render(request, 'discounts/discount_list.html', {'discounts': discounts})
