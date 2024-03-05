from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):

    bank_account = models.CharField(max_length=30, blank=True, null=True)

