
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import migrations
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
    first_name = models.CharField(
        max_length=150, validators=[MinLengthValidator(3)]
        )
    last_name = models.CharField(
        max_length=150, validators=[MinLengthValidator(3)]
        )
    email = models.EmailField(
        max_length=150, validators=[MinLengthValidator(3)]
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
    sunset_time = models.DateField(
        blank=True, null=True
        )
    
    USERNAME_FIELD = 'phone_number' 
    

    
    class Meta:
        db_table = 'users'

       
        # indexes = [
        #     GinIndex(
        #         SearchVector('first_name', 'last_name'), 
        #         name='user_first_last_gin_idx'
        #     ),
        # ]


