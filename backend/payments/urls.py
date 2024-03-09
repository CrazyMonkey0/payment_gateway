from django.urls import path
from . import views


urlpatterns = [
    # URL path to payment cart
    path('card/<int:order_id>/<uuid:link_uuid>', views.payment_card, name='card'), 
]
