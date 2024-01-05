from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Using authentication views provided by django
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # URL path to registration
    path('register/', views.register, name='register')
]
