from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from bank.models import MasterCard, Visa
from django.utils.translation import gettext_lazy as _


class CardForm(forms.Form):
    """
    A form for handling credit card information.

    Attributes:
        id_card (CharField): A field for entering the credit card number. It should be 16 characters long
            and contain only numeric characters.
        valid_until (CharField): A field for entering the expiration date of the credit card.
        cvc (CharField): A field for entering the Card Verification Code (CVC) of the credit card.

    Methods:
        clean_id_card(self): A method to validate the credit card number and determine its type (Visa or MasterCard).
    """

    id_card = forms.CharField(label='ID Card', max_length=16, min_length=16, widget=forms.TextInput(attrs={'placeholder': '1234567890123456'}),
                               validators=[RegexValidator(r'^[0-9]*$')])
    valid_until = forms.CharField(
        label=_('Expiry (MM/YYYY)'),
        widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'}),
        validators=[ 
            RegexValidator(
                regex=r'^(0[1-9]|1[0-2])\/\d{4}$',  # MM/YYYY format
                message=_("Enter a valid date in MM/YYYY format")
            )
        ]
    )
    cvc = forms.CharField(max_length=3, widget=forms.PasswordInput(attrs={'placeholder': '***'}), )

    def clean_id_card(self):
        """
        Clean method for validating the credit card number and checking if the card exists.

        Raises:
            forms.ValidationError: If the credit card number is not valid or the card does not exist.
        """
        id_card = self.cleaned_data.get('id_card')

        # Check if card starts with '4' (Visa) or '5' (MasterCard)
        if not id_card.startswith('4') and not id_card.startswith('5'):
            raise ValidationError(_("Unsupported card type"))

        # Check if the card exists in the database
        if id_card.startswith('4'):
            try:
                card = Visa.objects.get(id_card=id_card)
            except Visa.DoesNotExist:
                raise ValidationError(_("Card not found in our system."))
        elif id_card.startswith('5'):
            try:
                card = MasterCard.objects.get(id_card=id_card)
            except MasterCard.DoesNotExist:
                raise ValidationError(_("Card not found in our system."))
        
        return id_card
    
    def clean_cvc(self):
        """
        Clean method for validating the CVC (Card Verification Code).

        It compares the entered CVC against the stored CVC for the card.
        """
        cvc = self.cleaned_data.get('cvc')
        id_card = self.cleaned_data.get('id_card')

        # Ensure id_card is not None
        if not id_card:
            raise ValidationError(_("There is no compatibility between such a CVC and such a card"))

        # If the card starts with '4' (Visa), compare the entered CVC to the stored one
        if id_card.startswith('4'):
            card = Visa.objects.get(id_card=id_card)
            if card.cvc != cvc:
                raise ValidationError(_("Wrong CVC"))
        elif id_card.startswith('5'):  # If the card starts with '5' (MasterCard)
            card = MasterCard.objects.get(id_card=id_card)
            if card.cvc != cvc:
                raise ValidationError(_("Wrong CVC"))
                
        return cvc
    
    def clean_valid_until(self):
        """
        Clean method for validating the expiry date.

        It compares the entered expiry date against the stored valid_until date for the card.
        """
        valid_until = self.cleaned_data.get('valid_until')
        id_card = self.cleaned_data.get('id_card')

        # Ensure id_card is not None
        if not id_card:
            raise ValidationError(_("There is no match between such a date and such a card"))

        # If the card starts with '4' (Visa), compare the entered expiry date to the stored one
        if id_card.startswith('4'):
            card = Visa.objects.get(id_card=id_card)
            if card.valid_until != valid_until:
                raise ValidationError(_("Wrong Expiry"))
        elif id_card.startswith('5'):  # If the card starts with '5' (MasterCard)
            card = MasterCard.objects.get(id_card=id_card)
            if card.valid_until != valid_until:
                raise ValidationError(_("Wrong Expiry"))
                
        return valid_until
