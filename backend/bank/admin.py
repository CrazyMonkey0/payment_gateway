from django.contrib import admin
from .models import Bank, Visa, MasterCard, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


class VisaInline(admin.StackedInline):
    model = Visa
    extra = 0


class MasterCardInline(admin.StackedInline):
    model = MasterCard
    extra = 0


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',
                    'country', 'iban', 'balance']
    search_fields = ['first_name', 'last_name']
    list_filter = ['country']
    readonly_fields = ['iban']
    inlines = [MasterCardInline, VisaInline, TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['bank', 'first_name',
                    'last_name', 'transaction_type', 'amount', 'iban', 'date']
    search_fields = ['first_name', 'last_name', 'iban']
    list_filter = ['transaction_type',]


@admin.register(Visa)
class VisaAdmin(admin.ModelAdmin):
    list_display = ['bank', 'id_card',
                    'cvc', 'valid_until', 'is_valid']
    search_fields = ['id_card']
    list_filter = ['valid_until', 'is_valid']
    readonly_fields = ['id_card', 'cvc']


@admin.register(MasterCard)
class MasterCardAdmin(admin.ModelAdmin):
    list_display = ['bank', 'id_card',
                    'cvc', 'valid_until', 'is_valid']
    search_fields = ['id_card']
    list_filter = ['valid_until', 'is_valid']
    readonly_fields = ['id_card', 'cvc']
