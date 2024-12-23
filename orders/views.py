import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Order
from .forms import OrderForm
from carts.models import CartItem

# Create your views here.
@login_required(login_url='login')
def payments(requests):
    return render(requests, 'orders/payments.html')

@login_required(login_url='login')
def place_order(request):
    current_user = request.user

    # checking if cart items for the user is 0 then redirect the user to the store page
    cart_items = CartItem.objects.filter(user=current_user)
    cart_items_count = cart_items.count()

    if cart_items_count == 0:
        return redirect('store')
    

    # calculating grand_total and tax
    grand_total = tax = total = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)

    tax = total * 0.02
    grand_total = total + tax


    # if the user has cart items in their cart then proceed further
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        # Checking if the data iv valid in the form
        if form.is_valid():
            # creating an Order model instance
            data = Order()

            # Storing data from the form to the Order model instance (data, here)
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone_number = form.cleaned_data['phone_number']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']

            # storing additional data
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')

            # saving data with these informations to get the order id
            data.save()

            # Generating order number using the current year, month, day and the order id
            year = int(datetime.date.today().strftime('%Y'))    # YYYY
            month = int(datetime.date.today().strftime('%m'))   # MM
            day = int(datetime.date.today().strftime('%d'))     # DD
            date = datetime.date(year, month, day)  # YYYY-MM-DD
            current_date = date.strftime('%Y%m%d')  # YYYYMMDD
            
            order_number = current_date + str(data.id) # concatenating date and order id

            data.order_number = order_number

            # saving the data with the order number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order' : order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }

            # redirecting the user
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')

