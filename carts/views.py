from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from store.models import Product, ProductVariation

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
        # if authenticated user i.e., user logs in then fetch cart items depending on the user
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)

        # if user not logs in then fetch cart items depending on the session id from request
        else:
            # getting the cart and cart items from session id
            cart = Cart.objects.get(cart_id = _get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
        # iterating over cart items
        for cartitem in cart_items:
            total += cartitem.product.price * cartitem.quantity

    # if cartitem does not present
    except Cart.DoesNotExist:
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

def add_to_cart(request, product_id):   # passing product_id from product_details.html page
    # getting the current logged in user
    current_user = request.user

    # fetching the product
    product = Product.objects.get(id=product_id)

    # for storing product variations for a particular product
    product_variation = []

    if request.method == 'POST':
        # taking all key and value pair as if in future we introduce brand or any other variation, 
        # then also our code will work
        for key, value in request.POST.items():
            # checking if the key and value matches with the variation_catogory and variation_value of ProductVariation model
            try:
                variation = ProductVariation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)

            # if key and value doesnot match like csrfmiddlewaretoken, then do nothing and just skip
            except:
                pass
        
    # if user not logged in then getting the cart_id from the session else create cart
    if not current_user.is_authenticated:
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

    # if logged in user then getting the cart_items using the user
    if current_user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=current_user)

    # if not logged in user then getting the cart_items using the cart id
    else:
        # Getting all cart items from cart depending on product
        cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Checking for existance of the cart item
    is_cart_item_exists = cart_items.exists()

    # if cart item already exists in the cart
    if is_cart_item_exists:
        # for storing existing variations of cart items
        existing_variation_list = []
        # for storing the id of the existing variation in the existing_variation_list
        cart_item_id = []

        # looping over the cart items
        for item in cart_items:
            # getting all variations for a particular item in cart item
            existing_variation = item.product_variations.all()

            # appending existing_variation to existing_variation_list after converting queryset to a list
            existing_variation_list.append(list(existing_variation))

            # storing id of the particular cart item
            cart_item_id.append(item.id)


        # checking if the current product variation is in the exisitng product variation list
        if product_variation in existing_variation_list:
            # getting the iindex of the current variation from the existing variation list
            index = existing_variation_list.index(product_variation)

            # getting the id
            item_id = cart_item_id[index]

            # getting the cart item
            cart_item = CartItem.objects.get(product=product, id=item_id)

            # increasing the quantity of the particular variation
            cart_item.quantity += 1

            # saving the cart item
            cart_item.save()

        # if the current product variation is not in the existing product variation list
        else:
            # if user is logged in then creating the cart item using the user
            if current_user.is_authenticated:
                # creating a new cart item
                cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)

            # if user is not logged in then creating the cart item using the cart id
            else:
                # creating a new cart item
                cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)

            # if we have an variation of product
            if product_variation:
                # clear previous variation from cart item
                cart_item.product_variations.clear()
                
                # adding new variation to cart item
                cart_item.product_variations.add(*product_variation) # unpacking existing variation
            
            # saving the cart item
            cart_item.save()

    # if cart item does not exists in the cart
    else:
        # if user logged in then create using the user
        if current_user.is_authenticated:
            # creating cartitem object with quantity 1
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1,
            )
        # if user is not logged in then create using the cart id
        else:
            # creating cartitem object with quantity 1
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1,
            )

        # if we have an variation of product
        if product_variation:
            # clear previous variation from cart item
            cart_item.product_variations.clear()
            
            # adding new variation to cart item
            cart_item.product_variations.add(*product_variation) # unpacking existing variation
        
    # saving the cartitem
    cart_item.save()

    # taking the customer to the cart page
    return redirect('cart')

# implement minus button functionality  to decrement product quantity in cart page
def decrement_item_count(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    # if found cart_item with the cart, product and id then decrement ite's count by 1
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

        # if quantity is more than 1, decrement the qunatity by 1
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

        # if quantity is only 1, delete the cart item
        else:
            cart_item.delete()

    # if not found cart_item with the cart, product and id then do nothing
    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

    # deleting the item
    cart_item.delete()

    return redirect('cart')


@login_required(login_url='login')
def checkout(request):
    # code copied from cart view
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
    except Cart.DoesNotExist:
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

    return render(request, 'store/checkout.html', context)