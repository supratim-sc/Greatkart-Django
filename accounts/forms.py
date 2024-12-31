from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    # creating password and confirm_password fields as they are not ppart of Account model
    password = forms.CharField(
        widget = forms.PasswordInput()
    )

    confirm_password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'placeholder' : 'Confirm your password',    # way-1 to apply placeholder attribute
            }
        )
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    # Applying css class to fields mentioned in the Meta class
    def __init__(self, *args, **kwargs) -> None:
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            # applying 'form-control' class of bootstrap to every fields
            self.fields[field].widget.attrs['class'] = 'form-control'

            # Applying placeholder to each fields
            # spliting each field names with _ and then converting to capitalize case
            field_names = [word.capitalize() for word in field.split("_")]

            # Joining the converted field names with a space
            self.fields[field].widget.attrs['placeholder'] = f'Enter your {" ".join(field_names)}'

    
    # checking for password and confirm_passwords are same or not. For that overriding the clean() method of parent class.
    def clean(self):
        # This line calls the parent class's clean() method, ensuring that any other form validation from the parent class is executed before the custom validation. Then storing the data validated by parent class's validation logic.
        cleaned_data = super(RegistrationForm, self).clean()

        # retriving the value of the password field from the validated data.
        password = cleaned_data.get('password')

        # retriving the value of the confirm_password field from the validated data.
        confirm_password = cleaned_data.get('confirm_password')

        # checking if password and confirm_password field values, if not matched then raise error.
        if password != confirm_password:
            raise forms.ValidationError('Passwords does not match!!')



# Creating Form for User
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']    # as these 3 fields form Account model is used for user profile

    def __init__(self, *args, **kwargs) -> None:
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            # applying 'form-control' class of bootstrap to every fields
            self.fields[field].widget.attrs['class'] = 'form-control'

            # Applying placeholder to each fields
            # spliting each field names with _ and then converting to capitalize case
            field_names = [word.capitalize() for word in field.split("_")]

            # Joining the converted field names with a space
            self.fields[field].widget.attrs['placeholder'] = f'Enter your {" ".join(field_names)}'


# Creating Form for UserProfile
class UserProfileForm(forms.ModelForm):
    # Creating profile_picture field to hide the 'Profile Picture Currently' value
    profile_picture = forms.ImageField(
        required=False,
        error_messages={
            'invalid': ['Image Files Only'] # if invalid type of file uploaded then show error
        },
        widget=forms.FileInput, # this is used to hide the 'Profile Picture Currently' value as we are defining widget as forms.FileInput
    )
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'address_line_1', 'address_line_2', 'city', 'state', 'country'] 
        # these 6 fields from UserProfile model is used to store the details of User Profile along with the 3 fields from Account model

    def __init__(self, *args, **kwargs) -> None:
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            # applying 'form-control' class of bootstrap to every fields
            self.fields[field].widget.attrs['class'] = 'form-control'

            # Applying placeholder to each fields
            # spliting each field names with _ and then converting to capitalize case
            field_names = [word.capitalize() for word in field.split("_")]

            # Joining the converted field names with a space
            self.fields[field].widget.attrs['placeholder'] = f'Enter your {" ".join(field_names)}'