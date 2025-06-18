from django.contrib import admin
from django import forms
from decimal import Decimal
from django.http import HttpRequest, HttpResponse
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import Order, OrderItem
from discounts.models import Discount
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Any, Optional
import os

class OrderItemForm(forms.ModelForm):
    """Форма для позиции заказа с валидацией скидок."""

    class Meta:
        model = OrderItem
        fields = '__all__'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация формы с предзаполнением цены и фильтрацией скидок."""
        super().__init__(*args, **kwargs)
        if 'product' in self.fields and self.instance.product_id:
            self.fields['price'].initial = self.instance.product.price
            self.fields['discount'].queryset = Discount.objects.filter(
                product=self.instance.product,
                active=True
            )

    def clean(self) -> dict[str, Any]:
        """Проверка, что скидка соответствует выбранному товару."""
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        discount = cleaned_data.get('discount')
        
        if product and discount:
            if discount not in product.discounts.all():
                raise forms.ValidationError("Эта скидка не может быть применена к выбранному товару")
        return cleaned_data

class OrderItemInline(admin.TabularInline):
    """Инлайн-форма для позиции заказа в админке."""
    model = OrderItem
    form = OrderItemForm
    extra = 1
    fields = ("product", "quantity", "price", "discount", "final_price", "total_cost")
    readonly_fields = ("final_price", "total_cost")
    raw_id_fields = ("product",)

    @admin.display(description="Цена со скидкой")
    def final_price(self, obj: OrderItem) -> str:
        """Возвращает цену с учетом скидки."""
        if obj.price is None:
            return "0.00 руб."
        if obj.discount:
            discount_percent = Decimal(str(obj.discount.discount_percent))
            discount_amount = obj.price * discount_percent / Decimal('100')
            return f"{obj.price - discount_amount:.2f} руб."
        return f"{obj.price:.2f} руб."

    @admin.display(description="Сумма")
    def total_cost(self, obj: OrderItem) -> str:
        """Возвращает общую сумму по позиции."""
        final_price_str = self.final_price(obj)
        try:
            price = Decimal(final_price_str.split()[0])
            quantity = Decimal(str(obj.quantity)) if obj.quantity else Decimal('0')
            return f"{price * quantity:.2f} руб."
        except Exception:
            return "0.00 руб."

def export_order_pdf(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: Any) -> HttpResponse:
    """Экспорт заказов в PDF с табличным представлением."""
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="orders.pdf"'
    
    p: Canvas = Canvas(response, pagesize=A4)
    p.setFont("DejaVuSans", 14)
    width, height = A4
    margin = 20 * mm
    y_position = height - margin
    
    for order in queryset:
        p.setFont("DejaVuSans", 14)
        p.drawString(margin, y_position, f"Заказ #{order.id}")
        y_position -= 6 * mm
        
        p.setFont("DejaVuSans", 12)
        info_lines = [
            f"Клиент: {order.user.username}",
            f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}",
            f"Статус: {order.get_status_display()}"
        ]
        for line in info_lines:
            p.drawString(margin, y_position, line)
            y_position -= 5 * mm
        
        y_position -= 5 * mm
        
        data = [['Товар', 'Кол-во', 'Цена', 'Скидка', 'Сумма']]
        
        for item in order.items.all():
            discount = f"{item.discount.discount_percent}%" if item.discount else "-"
            row = [
                item.product.name,
                str(item.quantity),
                f"{item.price:.2f} руб.",
                discount,
                f"{item.price * item.quantity:.2f} руб."
            ]
            data.append(row)

        data.append(["ИТОГО:", "", "", "", f"{order.total_price:.2f} руб."])
        data.append(["Со скидкой:", "", "", "", f"{order.discounted_total:.2f} руб."])
        
        table = Table(data, colWidths=[80*mm, 20*mm, 30*mm, 20*mm, 30*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -3), (-1, -3), 1, colors.black),
        ]))
        
        table.wrapOn(p, width - 2*margin, height)
        table.drawOn(p, margin, y_position - table._height)
        y_position -= table._height + 15 * mm
        
        if y_position < margin:
            p.showPage()
            y_position = height - margin
    
    p.save()
    return response

export_order_pdf.short_description = "Экспорт заказов в PDF (таблица)"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов."""
    list_display = ("id", "user", "status", "created_date", "total_price", "discounted_total", "item_count")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at", "discounted_total", 'invoice')
    actions = [export_order_pdf]

    def save_formset(self, request: HttpRequest, form: forms.ModelForm, formset: forms.BaseInlineFormSet, change: bool) -> None:
        """Сохраняет позиции заказа с пересчётом итоговых сумм."""
        instances = formset.save(commit=False)
        order: Order = form.instance
        total = Decimal('0')
        discounted_total = Decimal('0')
        
        for instance in instances:
            if not instance.price and instance.product:
                instance.price = instance.product.price
            
            if instance.price and instance.quantity:
                price = instance.price
                quantity = Decimal(str(instance.quantity))
                final_price = price
                if instance.discount:
                    discount_percent = Decimal(str(instance.discount.discount_percent))
                    discount_amount = price * discount_percent / Decimal('100')
                    final_price = price - discount_amount
                
                total += price * quantity
                discounted_total += final_price * quantity
            instance.save()
        
        order.total_price = total
        order.discounted_total = discounted_total
        order.save()
        formset.save_m2m()

    @admin.display(description="Дата")
    def created_date(self, obj: Order) -> str:
        """Форматированная дата создания."""
        return obj.created_at.strftime("%d.%m.%Y")

    @admin.display(description="Общая сумма")
    def total_price(self, obj: Order) -> str:
        """Общая сумма заказа без скидки."""
        return f"{obj.total_price:.2f} руб." if obj.total_price else "0.00 руб."

    @admin.display(description="Итого со скидкой")
    def discounted_total(self, obj: Order) -> str:
        """Сумма заказа с учетом скидок."""
        if hasattr(obj, 'discounted_total'):
            return f"{obj.discounted_total:.2f} руб."
        
        total = Decimal('0')
        for item in obj.items.all():
            if item.price and item.quantity:
                price = Decimal(str(item.price))
                quantity = Decimal(str(item.quantity))
                if item.discount:
                    discount_percent = Decimal(str(item.discount.discount_percent))
                    price -= price * discount_percent / Decimal('100')
                total += price * quantity
        return f"{total:.2f} руб."

    @admin.display(description="Товаров")
    def item_count(self, obj: Order) -> int:
        """Количество товаров в заказе."""
        return obj.items.count()

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для позиций заказа."""
    list_display = ("id", "order", "product", "quantity", "price_display", "discount_info", "final_price_display", "total_cost_display")
    raw_id_fields = ("order", "product")
    list_filter = ("discount",)

    @admin.display(description="Цена")
    def price_display(self, obj: OrderItem) -> str:
        """Цена товара."""
        return f"{obj.price:.2f} руб." if obj.price else "0.00 руб."

    @admin.display(description="Скидка")
    def discount_info(self, obj: OrderItem) -> str:
        """Информация о скидке."""
        if obj.discount:
            return f"{obj.discount.name} ({obj.discount.discount_percent}%)"
        return "—"

    @admin.display(description="Цена со скидкой")
    def final_price_display(self, obj: OrderItem) -> str:
        """Цена товара с учетом скидки."""
        if obj.price is None:
            return "0.00 руб."
        if obj.discount:
            discount_percent = Decimal(str(obj.discount.discount_percent))
            return f"{obj.price * (Decimal('1') - discount_percent/Decimal('100')):.2f} руб."
        return f"{obj.price:.2f} руб."

    @admin.display(description="Сумма")
    def total_cost_display(self, obj: OrderItem) -> str:
        """Общая сумма за позицию."""
        final_price_str = self.final_price_display(obj)
        try:
            price = Decimal(final_price_str.split()[0])
            quantity = Decimal(str(obj.quantity)) if obj.quantity else Decimal('0')
            return f"{price * quantity:.2f} руб."
        except Exception:
            return "0.00 руб."
