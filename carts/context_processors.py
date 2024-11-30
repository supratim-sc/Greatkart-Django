from .models import Cart, CartItem
from .views import _get_cart_id

def get_cart_count(request):
    cart_count = 0

    # if admin url then return blank dictionary
    if 'admin' in request.path:
        return {}
    
    try:
        # if user logs in then fetch the cart item for that user
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)

        # is user not logged in then fetch cart items depending on the session id stored in the request
        else:
            # as there will be only one cart with a cart_id so get() is used
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            # as there may be more than one cart items associated with a cart id, so filter() is used
            cart_items = CartItem.objects.filter(cart=cart)
        # iterating over all cart_items and add all their quantity together
        for cart_item in cart_items:
            cart_count += cart_item.quantity

    # if cart not exists then do nothing
    except Cart.DoesNotExist:
        pass
    
    return {'cart_count' : cart_count}