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
    
    Security approach:
    - client_id and client_secret are VISIBLE but DISABLED (read-only)
    - Generated on first save, then shown to user
    - User can only edit: name and redirect_uris
    
    Flow:
    1. User fills name + redirect_uris → SUBMIT
    2. View generates client_id + client_secret
    3. Form shows SUCCESS page with client_id + client_secret (ONE TIME!)
    4. On edit: client_id + client_secret are VISIBLE but DISABLED
    """
    
    # Override fields to make them read-only when needed
    client_id = forms.CharField(
        label=_('Client ID'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',  # HTML5 readonly
        }),
        help_text=_('Your application\'s client ID. Use this to authenticate.')
    )
    
    client_secret = forms.CharField(
        label=_('Client Secret'),
        required=False,
        widget=forms.TextInput(attrs={  # NOT PasswordInput - user needs to COPY it!
            'class': 'form-control',
            'readonly': 'readonly',
        }),
        help_text=_('⚠️ Keep this secret! Copy it now - you won\'t see it again.')
    )
    
    class Meta:
        model = Application
        fields = ['name', 'client_id', 'client_secret', 'redirect_uris']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('My Application'),
            }),
            'redirect_uris': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('http://localhost:8000/callback\nhttp://example.com/oauth/callback'),
                'rows': 4,
            }),
        }
        help_texts = {
            'name': _('A user-friendly name for your application.'),
            'redirect_uris': _('Enter one URI per line. These are allowed callback URLs.'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add placeholders
        self.fields['name'].widget.attrs.update({
            'placeholder': _('Enter application name'),
        })
        self.fields['redirect_uris'].widget.attrs.update({
            'placeholder': _('Enter redirect URIs'),
        })
        
        # Logic for new vs existing applications
        if self.instance.pk:
            # EDIT MODE: Application already exists
            # client_id and client_secret are read-only
            self.fields['client_id'].disabled = True
            self.fields['client_secret'].disabled = True
            
            # Show current values
            self.fields['client_id'].initial = self.instance.client_id
            self.fields['client_secret'].initial = self.instance.client_secret
            
        else:
            # CREATE MODE: New application
            # Hide fields (will be filled after save)
            self.fields['client_id'].widget = forms.HiddenInput()
            self.fields['client_secret'].widget = forms.HiddenInput()
            
            # Set defaults for new application
            self.instance.client_type = Application.CLIENT_PUBLIC
            self.instance.authorization_grant_type = Application.GRANT_AUTHORIZATION_CODE  
    
    def clean_client_id(self):
        """
        Security: client_id cannot be changed by the user.
        Always return the value from the instance.
        """
        if self.instance.pk:
            return self.instance.client_id
        return self.cleaned_data.get('client_id', '')
    
    def clean_client_secret(self):
        """
        Security: client_secret cannot be changed by the user.
        Always return the value from the instance.
        """
        if self.instance.pk:
            return self.instance.client_secret
        return self.cleaned_data.get('client_secret', '')
    
    def clean_redirect_uris(self):
        """Validate the format of redirect URIs."""
        redirect_uris = self.cleaned_data.get('redirect_uris', '')
        
        if not redirect_uris.strip():
            raise forms.ValidationError(_('At least one redirect URI is required.'))
        
        # Validate each URI
        uris = [uri.strip() for uri in redirect_uris.split('\n') if uri.strip()]
        
        for uri in uris:
            if not uri.startswith(('http://', 'https://')):
                raise forms.ValidationError(
                    _('Invalid URI: "%(uri)s". Must start with http:// or https://'),
                    params={'uri': uri}
                )
        
        return redirect_uris
    
    def clean_name(self):
        """Validate the application name."""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise forms.ValidationError(_('Application name is required.'))
        
        if len(name) < 3:
            raise forms.ValidationError(_('Application name must be at least 3 characters.'))
        
        return name
