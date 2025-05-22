from email.mime import image
from django.db import models

from users.models import User

class Publications(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,blank=True, null=True )
    text = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now=True)
    image = models.ImageField(
        upload_to='publication_image', 
        null=True, blank=True
        )
    video = models.FileField(
        upload_to='publication_image', blank=True, 
        null=True
        )

