# Generated by Django 4.2.10 on 2025-02-03 06:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportroom',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='admin_rooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
