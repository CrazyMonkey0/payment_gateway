# Generated by Django 4.2.10 on 2024-03-15 09:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='bank_account',
        ),
        migrations.AddField(
            model_name='profile',
            name='iban',
            field=models.CharField(default='', max_length=32, validators=[django.core.validators.RegexValidator('^[0-9]*$')]),
        ),
    ]
