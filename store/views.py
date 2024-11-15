from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import Cart, CartItem
from carts.views import _get_cart_id

# Create your views here.
def store(request, category_slug=None):
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)
    
    products_count = products.count()
    context = {
        'products' : products,
        'products_count' : products_count,
    }

    return render(request, 'store/store.html', context)

def product_details(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # checking if the product is in the cart or not
        # as Cart is the foreignkry to the CartItem model, so we can access cart_id with __ (reverse relationship)
        is_cart_item = CartItem.objects.filter(cart__cart_id=_get_cart_id(request), product=product).exists()
    except Exception as e:
        raise e
    
    context = {
        'product' : product,
        'is_cart_item' : is_cart_item,
    }
    return render(request, 'store/product_details.html', context)