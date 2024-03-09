from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import Profile
import uuid

class Client(models.Model):
    """
    Model representing a client.

    Attributes:
    - name (CharField): Client's first name.
    - surname (CharField): Client's last name.
    - email (EmailField): Client's email address.
    """
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self) -> str:
        """
        Returns a string representation of the client.
        """
        return f"{self.name} {self.surname}"


class Product(models.Model):
    """
    Model representing a product.

    Attributes:
    - name (CharField): Product name.
    - quantity (PositiveIntegerField): Quantity of products.
    """
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        """
        Returns a string representation of the product.
        """
        return f"{self.name} X {self.quantity}"


class Order(models.Model):
    """
    Model representing an order.

    Attributes:
    - client (ForeignKey): Link to the Client model.
    - products (ManyToManyField): Link to the Product model.
    - profile (ForeignKey): Link to the User model.
    - total (DecimalField): Order total.
    - is_paid (BooleanField): Payment status.
    - date_of_order (DateTimeField): Order placement date.
    - date_of_payment (DateTimeField): Payment date for the order.
    - link (SlugField): Unique slug field for generating order links.
    """

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE,)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    date_of_order = models.DateTimeField(auto_now_add=True)
    date_of_payment = models.DateTimeField(null=True, blank=True)
    link = models.SlugField(max_length=100, unique=True, null=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the order.
        """
        return f"Order  {self.id} - {self.client}"
    
    def mark_as_paid(self):
        """
        Updates the payment date of the order to the current moment.
        """
        self.is_paid = True
        self.date_of_payment = timezone.now()
        self.save()
