from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Account


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