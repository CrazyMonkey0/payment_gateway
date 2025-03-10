from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # Using authentication views provided by django
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    # URL path to dashboard
    path('', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('why-us/', views.why_us, name='why_us'),
    path('team/', views.team, name='team'),
    # URL path to registration
    path('register/', views.register, name='register'),
    # URL path to show profil data about the user
    path('profile/', views.show_profile, name='show_profile'),
    # URL path to create profile and generated api-key
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('application/manage/', views.CustomRegistrationOAuth2.as_view(), name='manage_application'),
]
