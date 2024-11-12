from django.contrib import admin
from .models import Product

# Register your models here.
class CustomProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'updated_at']
    prepopulated_fields = {
        'slug' : ['name'],
    }

    def __str__(self) -> str:
        return self.name
    
admin.site.register(Product, CustomProductAdmin)
