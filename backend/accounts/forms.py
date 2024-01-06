from django import forms
from django.contrib.auth.models import User
from .models import Profile
import uuid


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
        model = User
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
        if User.objects.filter(email=cd['email']).exists():
            raise forms.ValidationError(
                'An account with such an email already exists.')
        return cd['email']


class ProfileForm(forms.ModelForm):
    """
    Django form to handle user profile data.

    Attributes:
        app (CharField): Field for entering the application name.
        bank_account (CharField): Field for entering the bank account number.

    Methods:
        save(self, commit=True):
            Method to save profile data. It also generates an API key if not assigned yet.

    """
    class Meta:
        model = Profile
        fields = ['app', 'bank_account']

    def save(self, commit=True):
        """
        Method to save profile data. It also generates an API key if not assigned yet.

        Parameters:
            commit (bool, optional): Flag indicating whether the data should be saved in the database. Default is True.

        Returns:
            Profile: Instance of the saved profile.
        """
        instance = super().save(commit=False)
        if instance.api_key is None:
            instance.api_key = str(uuid.uuid4())
            if commit:
                instance.save()
            return instance
