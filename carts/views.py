from django.shortcuts import render, redirect, get_object_or_404
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
    
    tax = total * 0.02
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
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

# implement minus button functionality  to decrement product quantity in cart page
def decrement_item_count(request, product_id):
    cart = Cart.objects.get(cart_id=_get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)

    # if quantity is more than 1, decrement the qunatity by 1
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    # if quantity is only 1, delete the cart item
    else:
        cart_item.delete()

    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)

    # deleting the item
    cart_item.delete()

    return redirect('cart')