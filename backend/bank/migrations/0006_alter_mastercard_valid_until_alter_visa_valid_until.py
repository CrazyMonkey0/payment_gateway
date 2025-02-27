# Generated by Django 4.2.10 on 2025-01-26 21:47

import bank.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0005_alter_mastercard_cvc_alter_visa_cvc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastercard',
            name='valid_until',
            field=models.CharField(default=bank.models.default_valid_until, max_length=7, validators=[django.core.validators.RegexValidator('^\\d{2}/\\d{4}$')]),
        ),
        migrations.AlterField(
            model_name='visa',
            name='valid_until',
            field=models.CharField(default=bank.models.default_valid_until, max_length=7, validators=[django.core.validators.RegexValidator('^\\d{2}/\\d{4}$')]),
        ),
    ]
