from django.contrib import admin
from .models import Order, Product, Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin class for the Client model.

    Fields:
    - name
    - surname
    - email
    List Display:
    - name
    - surname
    - email
    """
    fields = ["name", "surname", "email"]
    list_display = ["name", "surname", "email"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin class for the Product model.

    Fields:
    - name
    - quantity
    List Display:
    - name
    - quantity
    """
    fields = ["name", "quantity"]
    list_display = ["name", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin class for the Order model.

    Fields:
    - user
    - client
    - products
    - total
    - is_paid
    List Display:
    - user
    - client
    - total
    - is_paid
    - date_of_order
    - date_of_payment
    """
    fields = ["user", "client", "products", "total", "is_paid",]
    list_display = ["user", "client", "total",
                    "is_paid", "date_of_order", "date_of_payment"]
