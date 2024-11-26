from django.shortcuts import render, redirect
from django.contrib import messages, auth
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

            # showing success message
            messages.success(request, 'Registration Successful!!')

            # redirecting the user to registration page
            return redirect('register')

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