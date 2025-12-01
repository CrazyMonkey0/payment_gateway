from django import forms
from .models import Profile
from bank.models import Bank
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import Application
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
        
        Uses cd.get() to safely retrieve values, ensuring robustness even if
        the required fields validation hasn't run yet or a field is missing.
        """
        cd = self.cleaned_data
        password = cd.get('password')
        password2 = cd.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords are not identical.')
        
        return password2

    def clean_email(self):
        """
        Checks if there is an account with the same email address (case-insensitive)
        and normalizes the email to lowercase.
        """
        cd = self.cleaned_data
        email = cd['email'].lower()
        
        if Profile.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with such an email already exists.')
        
        return email


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
        if re.match(r'^[A-Z]{2}[0-9]+$', cd['iban']):
            try:
                Bank.objects.get(iban=cd['iban'])
            except Bank.DoesNotExist:
                raise forms.ValidationError("This IBAN does not exist.")
            return cd['iban']
        else:
            raise forms.ValidationError("Incorrect IBAN")


class CustomRegistrationFormOAuth2(forms.ModelForm):
    """
    OAuth2 Application Registration Form.

    Attributes:
        name (CharField): A field for entering the application's name.
        client_id (CharField): A field for entering the OAuth2 client ID.
        client_secret (CharField): A field for entering the OAuth2 client secret.
        redirect_uris (CharField): A field for entering redirect URIs.

    Methods:
        __init__(self): Initializes the form with the appropriate attributes and placeholders.
    """
    
    class Meta:
        model = Application  # Linking the form to the Application model
        fields = ['name', 'client_id', 'client_secret', 'redirect_uris']
        
    def __init__(self, *args, **kwargs):
        """
        Initializes the form and sets the appropriate field attributes.

        It also adds placeholders and sets the default values for 'client_type' and 'authorization_grant_type'.
        """
        super().__init__(*args, **kwargs)

        # Adding placeholder for 'name' field
        self.fields['name'].widget.attrs.update({
            'placeholder': _('Enter application name'),  # Placeholder translated
        })

        # Adding placeholder for 'redirect_uris' field
        self.fields['redirect_uris'].widget.attrs.update({
            'placeholder': _('Enter redirect URIs'),  # Placeholder translated
        })

        # Setting default values for 'client_type' and 'authorization_grant_type'
        self.instance.client_type = Application.CLIENT_PUBLIC
        self.instance.authorization_grant_type = Application.CLIENT_CONFIDENTIAL