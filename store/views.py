from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
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
        products = Product.objects.filter(is_available=True).order_by('id')
        
    # --- PAGINATION CONFIGURATION ---
    # creating object of paginator class
    paginator = Paginator(products, 3) # here 3 is the number of products per page

    # getting the page number from the url like "/?page="
    ''' here request.GET.get() is used as for first page we don't have '/?page=' 
    so, if used requset.GET['page] will show error, hence request.GET.get('page)'''
    page = request.GET.get('page')  

    # configuring products per page based on paginator configuration
    paged_products = paginator.get_page(page)
    
    products_count = products.count()
    context = {
        # 'products' : products,
        'products' : paged_products,     # instead of sending all products, sending paged_products only
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