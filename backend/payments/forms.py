from django import forms
from django.core.validators import RegexValidator
from bank.models import MasterCard, Visa

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

    id_card = forms.CharField(label='ID Card', max_length=16, min_length=16,
                               validators=[RegexValidator(r'^[0-9]*$')])
    valid_until = forms.DateField()
    cvc = forms.CharField(max_length=3)

    def clean_id_card(self):
        """
        Clean method for validating the credit card number and determining its type.

        Raises:
            forms.ValidationError: If the credit card number is not valid or its type is not supported.
        """
        id_card = self.cleaned_data['id_card']
        if id_card[0] == '4':
            # Visa
            try:
                Visa.objects.get(id_card=id_card) 
                return id_card
          
            except Visa.DoesNotExist:
                raise forms.ValidationError("Wrong id card")  

        elif id_card[0] == '5':
            # Master Card
            try:
                MasterCard.objects.get(id_card=id_card)
                return id_card
          
            except Visa.DoesNotExist:
                raise forms.ValidationError("Wrong id card")  
        else:
            raise forms.ValidationError("Unsupported card type")
