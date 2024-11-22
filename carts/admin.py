from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
class CustomCartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'created_at']

admin.site.register(Cart, CustomCartAdmin)


class CustomCartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'is_active']

admin.site.register(CartItem, CustomCartItemAdmin)