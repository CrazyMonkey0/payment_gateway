from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # URL path to registration
    path('register/', views.register, name='register')
]
