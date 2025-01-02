from django.contrib import admin

import admin_thumbnails

from .models import Product, ProductVariation, ReviewRatings, ProductGallery


# Register your models here.

# For showing thumbnails importing 'admin_thumbnails' and 
# then decorating the custom class with @admin_thumbnails.thumbnail('field_name_to_use_thumbnail')
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class CustomProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'updated_at']
    prepopulated_fields = {
        'slug' : ['name'],
    }
    inlines = [ProductGalleryInline]

    def __str__(self) -> str:
        return self.name
    
admin.site.register(Product, CustomProductAdmin)

class CustomProductVariationModel(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value', 'is_active']
    list_editable = ['is_active']

admin.site.register(ProductVariation, CustomProductVariationModel)

class CustomReviewRatingsAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'subject', 'review_first_10_words', 'ratings']
    search_fields = ['product', 'user', 'ratings']
    list_filter = ['product', 'ratings']
    list_per_page = 20

admin.site.register(ReviewRatings, CustomReviewRatingsAdmin)

admin.site.register(ProductGallery)