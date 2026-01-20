"""Модели приложения friends"""


from django.db import models

from users.models import User

class Friends(models.Model):
    
    STATUS_CHOISES = [
        ('pending','Отправлено'),
        ('accepted','Принято'),
        ('rejected','Отказано'),
    ]

    sender = models.ForeignKey(
        to = User, on_delete = models.CASCADE, 
        related_name = 'sender'
        )
    receiver = models.ForeignKey(
        to=User, on_delete=models.CASCADE, 
        related_name = 'receiver'
        )
    application_status = models.CharField(
        max_length = 15, choices=STATUS_CHOISES,
        db_index=True
        )

    class Meta:
        db_table = 'friends'
        indexes = [
            models.Index(
                fields=['sender','receiver'],name='idx_friends_sender_receiver')
        ]