from django import forms
from .models import Profile
from bank.models import Bank
import re


class UserRegistrationForm(forms.ModelForm):
    """
    Form for user registration.

    Attributes:
    - password (CharField): Field for entering the password.
    - password2 (CharField): Field for repeating and confirming the password.
    """

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        """
        Checks whether the passwords entered in the 'password' and 'password2' fields are identical.
        """
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords are not identical.')
        return cd['password2']

    def clean_email(self):
        """
        Checks if there is an account with the same email address.
        """
        cd = self.cleaned_data
        if Profile.objects.filter(email=cd['email']).exists():
            raise forms.ValidationError(
                'An account with such an email already exists.')
        return cd['email']


class ProfileForm(forms.ModelForm):
    """
    Form for creating or updating a user profile.

    Attributes:
    - first_name (CharField): The first name of the user.
    - last_name (CharField): The last name of the user.
    - iban (CharField): The IBAN (International Bank Account Number) of the user.
    """
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'iban']

    def clean_iban(self):
        """
        Custom clean method to validate IBAN.

        Raises:
            forms.ValidationError: If the provided IBAN does not exist in the database.

        Returns:
            str: Valid IBAN.
        """
        cd = self.cleaned_data
        if re.match(r'^[A-Z]{2}[0-9]*$', cd['iban']):
            try:
                Bank.objects.get(iban=cd['iban'])
            except Bank.DoesNotExist:
                raise forms.ValidationError("This IBAN does not exist.")
            return cd['iban']
        else:
            raise forms.ValidationError("Incorrect IBAN")
