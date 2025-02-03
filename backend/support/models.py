from django.conf import settings
from django.db import models
from django.apps import apps
import uuid


class SupportRoom(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    STATUS_CHOICES = [
        ('Created', 'CREATED'),
        ('Pending', 'PENDING'),
        ('Resolved', 'RESOLVED'),
        ('Closed', 'CLOSED')
    ]
    status = models.CharField(choices=STATUS_CHOICES, default='Created', max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_rooms')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_rooms', blank=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            UserModel = apps.get_model(settings.AUTH_USER_MODEL)
            super().save(*args, **kwargs)
            admin_users = UserModel.objects.filter(is_staff=True)
            self.admins.set(admin_users)  
        else:
            super().save(*args, **kwargs)


class Message(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(SupportRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
