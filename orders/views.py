import datetime
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string

from .models import Order, Payment, OrderProduct
from .forms import OrderForm
from carts.models import CartItem
from store.models import Product

# Create your views here.
@login_required(login_url='login')
def payments(request):
    # Getting JSON data from the request body set by using JavaScript
    body = json.loads(request.body)

    # Getting the amount paid for the order
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['order_id'])

    # Storing transaction details into Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transaction_id'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )

    # Saving the payment
    payment.save()

    # Saving payment to the Order table as payment is foreign key to Order table
    order.payment = payment
    # Changing the order status 
    order.is_ordered = True
    # Saving the order
    order.save()

    # Moving the cart items to OrderProduct table
    cart_items = CartItem.objects.filter(user = request.user)

    # iterating over the cart items and storing them to OrderProduct table
    for item in cart_items:
        # Creating OrderProduct object
        orderproduct = OrderProduct()

        # Saving details to the OrderProduct object
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True

        # Saving the OrderProduct object so that we can set the variations later
        orderproduct.save()

        # Getting the variations for the cart item
        product_variations = item.product_variations.all()
        # Setting the variations
        orderproduct.product_variations.set(product_variations)
        # Saving the product with its variations
        orderproduct.save()
        
        
        # Redue the quantity of the sold product
        # Getting the product using the cart item
        product = Product.objects.get(id=item.product_id)
        # Reducing the stock quantity
        product.stock -= item.quantity
        # Saving the product
        product.save()


    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to the customer
    # Subject of the email
    email_subject = 'Thank you for ordering with us!'

    # Creating email message
    email_message = render_to_string(       # rendering a template to a string, rather than returning an HTTP response
        'orders/order_received_email.html',
        {
            'user' : request.user,
            'order': order,
            'cart_items' : CartItem.objects.filter(user=request.user),
        }   # passing values to the template to make encoded link for activation
    )

    # the user given email address from the registation form
    to_email = request.user.email

    # Creating EmailMessage object with the set data
    send_email = EmailMessage(email_subject, email_message, to=[to_email])

    # Sending the mail
    send_email.send()

    # Send order number and transaction id back to the sendData() JS method on payemnts.html via JSON response

    return render(request, 'orders/payments.html')

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

