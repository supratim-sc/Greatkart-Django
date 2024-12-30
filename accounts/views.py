from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# EMAIL MESSAGE imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import requests

from .forms import RegistrationForm
from .models import Account

from carts.models import Cart, CartItem
from carts.views import _get_cart_id

from orders.models import Order

# Create your views here.
def register(request):
    # Checking if POST request comes in
    if request.method == 'POST':
        # getting all the data from the form using POST request
        form = RegistrationForm(request.POST)

        # checking if the data are valid or not
        if form.is_valid():
            # taking out all data from each inputs. as we are using forms, we need to use .cleaned_data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']

            # creating username by spliting the email and taking part before the @
            username = email.split('@')[0]

            # Creating the user object with the data we got. 
            # Here, we are using the create_user() method of MyAccountManager class using the Account class,
            # As MyAccountManager class is used as object in Account class
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)

            # assigning the phone_number to the user as phone_number is not a field in create_user() method
            user.phone_number = phone_number

            # saving the user
            user.save()

            # AUTHENTICATING user with activation link
            # getting the current site, which we will use in the email
            current_site = get_current_site(request)

            # Subject of the email
            email_subject = f'Please activate your {current_site} account'

            # Creating email message
            email_message = render_to_string(       # rendering a template to a string, rather than returning an HTTP response
                'accounts/account_verification_email.html',
                {
                    'user' : user,
                    'current_site' : current_site,
                    'encoded_user_id' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                }   # passing values to the template to make encoded link for activation
            )

            # the user given email address from the registation form
            to_email = email

            # Creating EmailMessage object with the set data
            send_email = EmailMessage(email_subject, email_message, to=[to_email])

            # Sending the mail
            send_email.send()

            # # showing success message
            # messages.success(request, 'Registration Successful!!')

            # # redirecting the user to registration page
            # return redirect('register')

            # instead of showing success message on the registration page we are taking user to a custom page and show message there
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()

    context = {
        'form' : form,
    }

    return render(request, 'accounts/register.html', context)

def login(request):
    # Checking if POST request
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticating the user with the provided email and password
        user = auth.authenticate(email=email, password=password)

        # checking if user is found with the provided credentials or not
        if user:
            # Assigning the cart items to the logged in user
            try:
                # getting the cart using the cart_id
                cart = Cart.objects.get(cart_id=_get_cart_id(request))

                # getting the cart items using the cart
                cart_items = CartItem.objects.filter(cart=cart)

                # if we have cart items then
                if cart_items.exists():
                    # for storing product variations for current product
                    product_variations = []

                    for item in cart_items:
                        # getting the variations of cart item
                        variation = item.product_variations.all()
                        # appending the variation to the list
                        product_variations.append(list(variation))

                    # getting cart items for the user
                    cart_items = CartItem.objects.filter(user=user)

                    # for storing the existing variations for product
                    existing_variation_list = []
                    # for storing the cart id
                    cart_item_id = []

                    # looping over the cart items for the user
                    for item in cart_items:
                        # getting the variations of item
                        existing_variation = item.product_variations.all()
                        # adding the existing variation to the exisitng_variation_list
                        existing_variation_list.append(list(existing_variation))
                        # storing the id of item
                        cart_item_id.append(item.id)

                    # looping over the current variation list to check if it is in existing_variation_list
                    for variation in product_variations:
                        # if the variation is in the existing variation
                        if variation in existing_variation_list:
                            # getting the index of the variation
                            index = existing_variation_list.index(variation)
                            # getting the id at that index
                            item_id = cart_item_id[index]
                            # getting the cart item using the id
                            cart_item = CartItem.objects.get(id=item_id)
                            # increasing the quantity of that variation
                            cart_item.quantity += 1
                            # assigning the user to the cart_item
                            cart_item.user = user
                            # saving the cart item
                            cart_item.save()

                        # if the variation is not in the exiting variation then
                        else:
                            # getting the items using cart id from session
                            cart_items = CartItem.objects.filter(cart=cart)
                            # looping over the cart items
                            for item in cart_items:
                                # assigning the logged in user to the cart item
                                item.user = user
                                # saving the cart item
                                item.save()
            except:
                pass

            # if user found, then logging in the user
            auth.login(request, user)

            # showing login successful message
            messages.success(request, 'Logged in successfully!!')

            # this will grab the URL from where we are coming
            url = request.META.get('HTTP_REFERER')  # http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/

            try:
                # The line query = requests.utils.urlparse(url).query is used to extract the query string from a URL. 
                # taking the part after the ? from the URL we are coming from
                query = requests.utils.urlparse(url).query  # next=/cart/checkout/

                # query.split('&'): splits the query into parts based on the & character. In this case, since there is only one key-value pair (next=/cart/checkout/), the split results in a list: ['next=/cart/checkout/'].
                # x.split('='): Each item in the list is then split by the = character to separate the key and the value. The result would be a list like ['next', '/cart/checkout/'].
                # dict(...): The dict() function then converts the list of key-value pairs into a dictionary, where 'next' is the key and '/cart/checkout/' is the value
                # For example, for a more complex query string like "next=/cart/checkout/&user=JohnDoe", the result would be: {'next': '/cart/checkout/', 'user': 'JohnDoe'}
                params = dict(x.split('=') for x in query.split('&'))   # {'next': '/cart/checkout/'}

                if 'next' in params:
                    # if we have next in URL then redirecting the user to the next query page
                    return redirect(params['next'])
                
            except:
                pass

            # redirecting the user to the home page
            return redirect('dashboard')
            
        
        # if user not founf with the provided credentials
        else:
            # showing error message
            messages.error(request, 'Invalid credentials!!')

            # taking back the user to the login page again
            return redirect('login')
        
    
    return render(request, 'accounts/login.html')


# this decorator will check for if the user is logged in or not, 
# if logged in the run the function logout() else redirect user to login page url
@login_required(login_url='login')
def logout(request):
    # logging out the user
    auth.logout(request)

    # showing logout message
    messages.success(request, 'Logged out successfully!!')

    # reddirecting the user to the login page after logging out
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(ValueError, TypeError, OverflowError, Account.DoesNotExist):
        user = None
    
    # if user is not None and the token is valid
    if user and default_token_generator.check_token(user, token):
        # setting the user to active user
        user.is_active = True

        # saving the user
        user.save()

        # displaying success message
        messages.success(request, 'Congratulations! Your account is activated. You can login.')

        # redirecting the user to login page
        return redirect('login')
    
    # if the user is None or token is not valid or token expired
    else:
        # showing error message
        messages.error(request, 'Invalid activation link')

        # redirecting the user to registration page
        return redirect('register')
    


@login_required(login_url='login')
def dashboard(request):
    # Fetching orders for the logged in user
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    context = {
        'orders_count' : orders_count,
    }

    return render(request, 'accounts/dashboard.html', context)



def forgotPassword(request):
    # checking if the request method is POST
    if request.method == 'POST':
        # getting the user provided email
        email = request.POST['email']
        
        # Checking if the user with the email provided exists or not
        if Account.objects.filter(email__exact=email).exists():

            # getting the user
            user = Account.objects.get(email__exact=email)

            # getting the current site, which we will use in the email
            current_site = get_current_site(request)

            # Subject of the email
            email_subject = f'Reset password for your {current_site} account'

            # Creating email message
            email_message = render_to_string(       # rendering a template to a string, rather than returning an HTTP response
                'accounts/forgot_password_email.html',
                {
                    'user' : user,
                    'current_site' : current_site,
                    'encoded_user_id' : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                }   # passing values to the template to make encoded link for activation
            )

            # the user given email address from the registation form
            to_email = email

            # Creating EmailMessage object with the set data
            send_email = EmailMessage(email_subject, email_message, to=[to_email])

            # Sending the mail
            send_email.send()

            # Displaying success message
            messages.success(request, 'Password reset link has been sent to your email ' + email)

            # Taking the user to login page
            return redirect('login')

        # if user with the provided email does not exists then
        else:
            # showing an error message
            messages.error(request, 'Account does not exists!!')

            # redirecting the user to reset password page
            return redirect('forgotPassword')

    return render(request, 'accounts/forgot_password.html')


def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(ValueError, TypeError, OverflowError, Account.DoesNotExist):
        user = None
    
    # if user is not None and the token is valid
    if user and default_token_generator.check_token(user, token):
        # setting uid in the session
        request.session['uid'] = uid

        # displaying success message
        messages.success(request, 'Please reset your password')

        # redirecting the user to reset pqassword page
        return redirect('resetPassword')
    
    # if the user is None or token is not valid or token expired
    else:
        # showing error message
        messages.error(request, 'Invalid password change link')

        # redirecting the user to login page
        return redirect('login')


def resetPassword(request):
    # if post the password reset form
    if request.method == 'POST':
        # storing the password and confirm_password values
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # if passwords fo not match
        if password != confirm_password:
            # showing error message
            messages.error(request, 'Passwords do not mathch!!')

            # redirecting the user to the reset_password page
            return redirect('resetPassword')
        
        # if password matches then retrieve the uid from the session of request object
        uid = request.session.get('uid')
        
        # retrieving the user object
        user = Account.objects.get(pk=uid)

        # setting the new password for the user
        user.set_password(password)
        
        # saving the user with the new changed password
        user.save()

        # deleting the uid from the session after changing the user password
        del request.session['uid']

        # printing success message
        messages.success(request, 'Password changed successfully')

        # redirecting the user to login page
        return redirect('login')


    return render(request, 'accounts/reset_password.html')