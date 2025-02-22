# Generated by Django 4.2.10 on 2024-04-18 10:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0004_alter_transaction_iban'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastercard',
            name='cvc',
            field=models.CharField(max_length=3, validators=[django.core.validators.RegexValidator('^[0-9]*$')]),
        ),
        migrations.AlterField(
            model_name='visa',
            name='cvc',
            field=models.CharField(max_length=3, validators=[django.core.validators.RegexValidator('^[0-9]*$')]),
        ),
    ]
