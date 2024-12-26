from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone_number', 'email', 'order_total', 'status', 'is_ordered']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone_number', 'email']
    list_per_page = 20

admin.site.register(Payment)

admin.site.register(Order, CustomOrderAdmin)

admin.site.register(OrderProduct)