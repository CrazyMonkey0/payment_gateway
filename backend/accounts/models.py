from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class Profile(AbstractUser):
    iban = models.CharField(max_length=32, default="", validators=[
                            RegexValidator(r'^[A-Z]{2}[0-9]*$')])
    url_feedback = models.SlugField(default="")