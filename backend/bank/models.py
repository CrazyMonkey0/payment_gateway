from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
from datetime import timedelta


def default_valid_until():
    """
    Returns a default expiration date for cards.

    This function calculates the default expiration date for cards by adding
    730 days (2 years) to the current date and time obtained from the timezone module.

    Returns:
        datetime: The default expiration date for cards.
    """
    return timezone.now() + timedelta(days=730)


class Bank(models.Model):
    """
    Represents a bank entity.

    Attributes:
        first_name (CharField): First name of the account holder.
        last_name (CharField): Last name of the account holder.
        country (CharField): Country of the bank.
        iban (CharField): International Bank Account Number.
        balance (DecimalField): Current balance of the account.
    """
    COUNTRY_CHOICES = [
        ('PL', 'Poland'),
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
    ]

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    iban = models.CharField(max_length=32, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} | Balance: {self.balance}$"


class Transaction(models.Model):
    """
    Represents a transaction entity.

    Attributes:
        bank (ForeignKey): Bank associated with the transaction.
        first_name (CharField): First name of the account holder.
        last_name (CharField): Last name of the account holder.
        transaction_type (CharField): Type of the transaction.
        amount (DecimalField): Amount involved in the transaction.
        iban (CharField): International Bank Account Number.
        date (DateTimeField): Date and time of the transaction.
    """
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'deposit'),
        ('WITHDRAWAL', 'withdrwal'),
        ('TRANSFER', 'transfer'),
    ]

    bank = models.ForeignKey(
        Bank, on_delete=models.CASCADE, related_name='transactions')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    iban = models.CharField(max_length=32, unique=True)
    date = models.DateTimeField(
        auto_now_add=True, verbose_name="Transaction date")

    def __str__(self) -> str:
        return f"Name: {self.first_name} {self.last_name} | ID bank: {self.iban} | Amount: {self.amount}$"


class Card(models.Model):
    """
    Represents a card entity.

    Attributes:
        bank (OneToOneField): Bank associated with the card.
        id_card (CharField): Card identifier.
        cvc (CharField): Card Verification Code.
        valid_until (DateTimeField): Expiry date of the card.
        is_valid (BooleanField): Status of the card's validity.
    """
    bank = models.OneToOneField(Bank, on_delete=models.CASCADE)
    id_card = models.CharField(max_length=16,
                               validators=[RegexValidator(r'^[0-9]*$'), MinLengthValidator(16)], unique=True)
    cvc = models.CharField(max_length=16, validators=[
                           RegexValidator(r'^[0-9]*$')])
    valid_until = models.DateTimeField(default=default_valid_until)
    is_valid = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Visa(Card):
    """
    Represents a Visa card.

    Attributes:
        logo (CharField): Logo of the Visa card.
    """
    logo = models.CharField(max_length=20, default='Visa')

    def __str__(self) -> str:
        return f"{self.bank.first_name} {self.bank.last_name}"


class MasterCard(Card):
    """
    Represents a MasterCard.

    Attributes:
        logo (CharField): Logo of the MasterCard.
    """
    logo = models.CharField(max_length=20, default='Master Card')

    def __str__(self) -> str:
        return f"{self.bank.first_name} {self.bank.last_name}"
