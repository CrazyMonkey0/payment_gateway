from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile


fields = list(UserAdmin.fieldsets)
fields[0] = (None, {'fields': ('username', 'password', 'iban')})
UserAdmin.fieldsets = tuple(fields)


admin.site.register(Profile, UserAdmin)
