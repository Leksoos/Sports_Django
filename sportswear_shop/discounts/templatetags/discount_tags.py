from django import template

register = template.Library()

@register.filter
def discount_price(price, percent):
    try:
        return "%.2f" % (float(price) * (1 - float(percent) / 100))
    except Exception:
        return price