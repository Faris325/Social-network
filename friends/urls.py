"""
URL configuration for sh project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from atexit import register
from django.contrib import admin
from django.urls import path
from friends import views

app_name = 'friends'

urlpatterns = [
    path('add-friends/', views.AddFriend.as_view(), 
         name='add-friend'
         ),
    path('friends/', views.FriendsList.as_view(), 
         name='friends'
         ),
    path('profile/friends/accept',views.FriendAccept.as_view(),
         name = 'friend-accept'),
    path('profile/friends/cancellation',views.FriendCancellation.as_view(),
         name = 'friend-cancellation'),
    path('profile/friends/reject',views.FriendReject.as_view(),
         name = 'friend-reject'),
    path('profile/friends/delete',views.FriendDelete.as_view(),
         name = 'friend-delete'),
     path('profile/friends/<int:id>/',views.FriendProfileView.as_view(),
         name = 'friend-profile'),
               
    ]
    
    