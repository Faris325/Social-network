from email.mime import application
from django.db import models
from users.models import User

class Friends(models.Model):
    STATUS_CHOISES = [
        ('pending','Отправлено'),
        ('accepted','Принято'),
        ('rejected','Отказано'),
    ]

    sender = models.ForeignKey(
        to = User, on_delete = models.CASCADE, related_name = 'sender'
        )
    receiver= models.ForeignKey(
        to= User, on_delete=models.CASCADE, related_name = 'receiver'
        )
    application_status = models.CharField(
        max_length = 15, choices=STATUS_CHOISES)

    class Meta:
        db_table = 'friends'