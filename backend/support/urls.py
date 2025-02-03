from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chats, name='chats'),
    path('create-room/', views.create_room, name='create_room'),
]
