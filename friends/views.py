from email.mime import application
from django.shortcuts import render
from django.views import View
from friends.models import Friends

class AddFriend(View):

    def post(self, request):

        sender = request.user
        receiver = int(request.POST.get('receiver'))

        Friends.objects.create(
            sender=sender, receiver=receiver, 
            application_status = 'pending'
            )
        