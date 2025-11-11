from django.urls import path
from publications import views

app_name = 'publications'

urlpatterns = [
    path('publications/', views.PublicationsView.as_view(), 
         name='publication'
         ),
    path('publications-delete/', views.PublicationDelete.as_view(), 
         name='publication-delete'
         ),
    path('publications-like/', views.PublicationLike.as_view(), 
     name='publication-like'
     ),

    path('comments/', views.PublicationComments.as_view(), 
     name='publication-comments'
     ),
     path('comments-comment/', views.PublicationComments.as_view(), 
     name='add-comments'
     ),
     
]