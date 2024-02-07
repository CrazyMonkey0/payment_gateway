from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [

    path('orders/', views.OrderAPIView.as_view(), name='order-api'),
]
