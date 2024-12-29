from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])

    def __str__(self) -> str:
        return self.name
    

# Custom PRoduct Variation Manager
class ProductVariationManager(models.Manager):  # inherits from models.Manager, which is the base class for Django's model managers.
    # override the default query behavior by calling super().filter() to apply custom filters based on the variation_category and is_active fields.
    def colors(self):
        return super().filter(variation_category='color', is_active=True)
    
    # override the default query behavior by calling super().filter() to apply custom filters based on the variation_category and is_active fields.
    def sizes(self):
        return super().filter(variation_category='size', is_active=True)
    


product_variation_category_choices = (
    ('color', 'Color'),
    ('size', 'Size'),
)


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=50, choices=product_variation_category_choices)
    variation_value = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom Manager is assigned to the objects attribute, which means any query on ProductVariation.objects will use ProductVariationManager's methods, not the default methods. 
    # So, essentially extending the model's functionality with custom query methods, improving code reusability and readability.
    objects = ProductVariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRatings(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(blank=True)
    ratings = models.FloatField()
    ip = models.CharField(max_length=10, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ReviewRating"
        verbose_name_plural = "ReviewRatings"

    def __str__(self):
        return self.subject
    
    def review_first_10_words(self):
        # Split the content into words and join the first 10
        return ' '.join(self.review.split()[:10]) + '...'