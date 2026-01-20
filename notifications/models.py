"""Модели для приложения notifications"""


from django.db import models

from users.models import User

class Notifications(models.Model):
    
    TYPE_CHOISES = [
        ('message_response','Сообщение'),
        ('friend_request','Запрос в друзья'),
        ('friend_response','Ответ о дружбе '),
    ]

    type = models.CharField(choices = TYPE_CHOISES)
    user = models.ForeignKey(to = User, on_delete = models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'notifications'
