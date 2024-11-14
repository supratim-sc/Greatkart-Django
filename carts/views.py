from django.shortcuts import render, redirect
from .models import Cart, CartItem
from store.models import Product

# Create your views here.
def _get_cart_id(request):
    # getting the from session_key
    cart = request.session.session_key

    # if there is no session_key exists then create one
    if not cart:
        # creating a new session
        cart = request.session.create()

    # returning the cart
    return cart

def cart(request):
    total = 0
    cart_items = None
    try:
        # getting the cart items
        cart = Cart.objects.get(cart_id = _get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        # iterating over cart items
        for cartitem in cart_items:
            total += cartitem.product.price * cartitem.quantity
    # if cartitem does not present
    except CartItem.DoesNotExist:
        # do nothing and use the predefined values 0 and None
        pass
    
    context = {
        'total': total,
        'cart_items': cart_items,
    }

    return render(request, 'store/cart.html', context)

# creating a private function to get the cart_id. Here _ means private function

def add_to_cart(request, product_id):   # passing product_if from product_details.html page
    # fetching the product
    product = Product.objects.get(id=product_id)

    # getting the cart, if not then create cart
    try:
        # getting the cart object
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
    # if cart is not present
    except Cart.DoesNotExist:
        # creating a new cart object
        cart = Cart.objects.create(
            cart_id = _get_cart_id(request)
        )
        cart.save()

    # Assigning items to cart
    try:
        # getting the cartitem object
        cartitem = CartItem.objects.get(product=product, cart=cart)
        # incrementing the quantity of item if already exists
        cartitem.quantity += 1

    # if cartitem object is not present then creating one
    except CartItem.DoesNotExist:
        # creating cartitem object with quantity 1
        cartitem = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1,
        )
        
    # saving the cartitem
    cartitem.save()

    # taking the customer to the cart page
    return redirect('cart')