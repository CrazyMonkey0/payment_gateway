# Generated by Django 4.2.10 on 2024-03-07 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='link',
            field=models.SlugField(max_length=100, null=True, unique=True),
        ),
    ]
