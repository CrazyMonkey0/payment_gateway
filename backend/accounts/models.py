from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    Model representing a user profile.

    Attributes:
    - user (OneToOneField): Link to the User model.
    - api_key (CharField): API key associated with the user's profile (optional).
    - bank_account (CharField): Bank account number associated with the user's profile (optional).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    app = models.CharField(
        max_length=255, unique=True, blank=True, null=True)
    api_key = models.CharField(
        max_length=255, unique=True, blank=True, null=True)
    bank_account = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the user profile.

        Example:
        If the user's username is "john_doe", the method will return "john_doe".
        """
        return f'User profile {self.user.username}'
