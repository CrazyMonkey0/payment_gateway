from django import forms
from django.contrib.auth.models import User


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
