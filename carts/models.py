from django.db import models
from store.models import Product, ProductVariation
from accounts.models import Account

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.cart_id
    
class CartItem(models.Model):
    # to assigning the user after uer login
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # as many products can have same variation and same product can have various variations
    product_variations = models.ManyToManyField(ProductVariation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    # this calculates the subtotal price for each cart items
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return self.product.name