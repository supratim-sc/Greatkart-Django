from django.contrib import admin
from django.utils.html import format_html
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug' : ['name']
    }
    list_display = ['name', 'slug', 'show_image']

    # Custom function to show category image
    def show_image(self, category):
        # if category has any image
        if category.image:
            return format_html(f'<img src="{category.image.url}" alt="{category.name}" width="100" height="100" style="object-fit:contain">')
        # if category does not have any image
        else:
            return 'No image'
    
admin.site.register(Category, CategoryAdmin)