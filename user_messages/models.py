from django.db import models

from users.models import User

class Messages(models.Model):
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    recipient = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

