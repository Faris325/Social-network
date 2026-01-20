"""Модели приложения users"""


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector

class User(AbstractUser):
    
    """Модель пользователя
        
    В этой модели вместо поля 'username' используется 'phone_number'. Для 
    этого поле 'username' отключено через 'username = None', а 'USERNAME_FIELD' 
    установлено в 'phone_number'. Это позволяет Django использовать номер 
    телефона для аутентификации, например, метод 'authenticate' будет искать 
    пользователя по номеру телефона вместо имени пользователя.

    """

    username = None
    nickname = models.CharField(
        max_length=28, validators=[MinLengthValidator(3)]
        )
    phone_number = models.CharField(
        max_length=15, unique=True
        )
    image = models.ImageField(
            blank=True, upload_to='user_images'
            )
    user_status = models.CharField(
            max_length=50, blank=True, 
            null=True
            )
    last_seen = models.DateTimeField(
        auto_now = True,blank=True, 
        null=True
        )
    
    time_zone = models.CharField(
        blank = True, null = True, 
        default = 'UTC'   
    )
    

    
    USERNAME_FIELD = 'phone_number' 
    

    
    class Meta:
        db_table = 'users'
        indexes = [
            GinIndex(
                SearchVector("nickname",config="simple"),
                name="nicname_User_vector_idx"
            )
        ]

       
 

