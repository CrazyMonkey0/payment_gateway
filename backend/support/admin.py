from django.contrib import admin
from .models import SupportRoom, Message

@admin.register(SupportRoom)
class SupportRoomAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'title',
                    'status', 'created_at', 'user']
    search_fields = ['user', 'title', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['content', 'timestamp',
                    'chat', 'sender']
    search_fields = ['sender', 'chat', 'timestamp']