from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin class for the Profile model.

    Attributes:
    - fields (list): List of fields to be displayed and edited in the admin panel.
    - list_display (list): List of fields to be displayed in the list view of the admin panel.
    """
    fields = ['user', 'api_key', 'bank_account']
    list_display = ['user', 'user_email', 'api_key', 'bank_account']

    def user_email(self, obj):
        """
        Returns the email of the associated user.
        """
        return obj.user.email

    user_email.short_description = 'User Email'
