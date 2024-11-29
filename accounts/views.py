from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# EMAIL MESSAGE imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from .models import Account

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
            # if user found, then logging in the user
            auth.login(request, user)

            # showing login successful message
            messages.success(request, 'Logged in successfully!!')

            # redirecting the user to the home page
            return redirect('login')
        
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