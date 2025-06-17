
from django.db import models

from users.models import User

class Publications(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True )
    text = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now=True)
    media = models.FileField(
        upload_to = 'publications_media', blank=True, 
        null = True )

