from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password):
        # checking if email and username is provided by the user while creating account
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        
        # Creating the user
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        # setting the password
        user.set_password(password)
        # saving the user
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, username, email, password):
        # using 'create_user()' method, defined before this, to create superuser as some fields are common
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            password = password, 
        )

        # giving the permissions to the admin user
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True

        # saving the user
        user.save(using = self._db)
        return user

class Account(AbstractBaseUser):
    # fields for normal user
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=10, blank=True)

    # fields for admin user
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # changing the loging method from username to email
    USERNAME_FIELD = 'email'

    # which fields are required to create a user, 
    # email not passed as it is required to login so not need to again mention
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # To create account for user or superuser we are using the 'MyAccountManager' class object
    objects = MyAccountManager()

    def __str__(self) -> str:
        return self.email
    
    # madatory permission lookup method
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin    # if admin user then have all permissions
    
    # mandatory permission lookup method
    def has_module_perms(self, add_label):
        "Does the user have permissions to view the app `app_label`?"
        return True
    
    # for reference go to: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#:~:text=for%20more%20details.-,Custom%20users%20and%20permissions,-%C2%B6