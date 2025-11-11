
from django.db import models

from users.models import User

class Publications(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, 
                             null=True 
                             )
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    media = models.FileField(
        upload_to = 'publications_media', blank=True, 
        null = True )
    liked_by = models.ManyToManyField(User, related_name="liked_publication" )
    topic = models.TextField()


    class Meta:
        db_table = 'publications'


class Comments(models.Model):
    publication = models.ForeignKey(Publications, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)