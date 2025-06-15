from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__id', 'transaction_id')
    readonly_fields = ('created_at', 'transaction_id')
    raw_id_fields = ('order',)
    date_hierarchy = 'created_at'