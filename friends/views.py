"""Модуль с контроллерами для приложения friends

   AddFriend - Контроллер для добавления в друзья
   FriendsList - Контроллер для вывода друзей пользователя, а так же заявок
   FriendAccept - Контроллер для принятия заявок в друзья
   FriendCancellation - Контроллер для отмены исходящяй заявки в друзья
   FriendReject - Контроллер для отмены входящяй заявки в друзья
   FriendDelete - Контроллер для удаления друга 
   FriendProfileView - Контроллер для отображения профиля

"""
import json

from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case
from django.db.models import When
from django.db.models import F
from django.db.models import IntegerField
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync  

from notifications.models import Notifications
from users.models import User
from friends.models import Friends
from publications.models import Publications

class AddFriend(LoginRequiredMixin, View):

    """Контроллер для отправки запроса в друзья 
    """

    def post(self, request):
        """
            Данные отправляющего(sender) берутся из request, а для получаешего
            берется из формы при выводе пользователей.
            сохраняется по итогу сохраняется запись в таблице с отправляющим,
            заявку, принимающим, а так же статус запроса, в данном случае это 
            будет pending (ожидающий)
        """
        data = json.loads(request.body)
        sender = request.user
         
        receiver = User.objects.get(id = data['receiver'])
        if not Friends.objects.filter(
            sender = sender, receiver=receiver,
            application_status = 'pending'
            ): # чтобы не повторять заявку

            Friends.objects.create(
                sender=sender, receiver=receiver,
                application_status = 'pending'
                )
            
            Notifications.objects.create(type = 'pending', user=receiver,)
        else:
            return JsonResponse({'status': 'ok'})

        channel_layer = get_channel_layer()    
        async_to_sync(channel_layer.group_send)(
        f"user_{receiver.id}",  # группа пользователя
        {
            "type": "notify_friend_add",  
            "message": f"Вас хочет добавить в друзья пользователь {sender.last_name} {sender.first_name}",
            "sender_id": sender.id
        }
    )
        return JsonResponse({'status': 'ok'})


class FriendsList(LoginRequiredMixin, ListView):

    """
    Контроллер для вывода друзей пользователя, входящих и исходящих запросов 
    """

    model = Friends
    template_name = 'friends.html'
    context_object_name = 'friends'

    def get_queryset(self):
        """ Получение кварисета пользователей
        """
        friends_id = list(Friends.objects.filter(
                Q(sender=self.request.user, application_status='accepted') |
                Q(receiver=self.request.user, application_status='accepted')
                ).annotate(friend_id=Case(
                    When(sender=self.request.user, then=F('receiver_id')),
                    When(receiver=self.request.user, then=F('sender_id')),
                    output_field=IntegerField()
                )
            ).values_list('friend_id', flat=True)
        )
        

        return User.objects.filter(id__in=friends_id)
    
    def get_context_data(self, **kwargs):
        """Метод для получения кварисетов входящих и исходящих запросов в 
           друзья 
        """
        incomings = Friends.objects.filter(
            receiver=self.request.user, application_status = 'pending'
            ).select_related('sender')
            
        outgoings = Friends.objects.filter(
        Q(sender=self.request.user, application_status='pending') |
        Q(sender=self.request.user, application_status='rejected')
        ).select_related('receiver')

        kwargs['incomings'] = incomings
        kwargs['outgoings'] = outgoings
        return super().get_context_data(**kwargs)
    

class FriendAccept(LoginRequiredMixin, View):
        
        """Контроллер для принятия заявки в друзья
        """
        
        def post(self, request):
            """Принимает запрос в друзья и удаляет входящую заявку
               Если был отправлены запросу друг другу, то как кто то примет, 
               заявки входящие удалятся у 2 
            """
            data = json.loads(request.body)

            receiver = request.user
            sender = User.objects.get(id = data['user_id'])

            Friends.objects.create(
                sender = sender, receiver = receiver, 
                application_status = 'accepted'
                )
            
            Friends.objects.filter(
                Q(sender=sender, receiver = receiver,
                application_status = 'pending')|
                Q(sender=receiver, receiver = sender, 
                application_status = 'pending')).delete()
         
            return JsonResponse({'status': 'ok'})

class FriendCancellation(LoginRequiredMixin, View):

    """Контроллр для отмены исходящей заявки в друзья"""

    def post(self, request):
        sender = request.user
        data = json.loads(request.body)
        receiver = User.objects.get(id = data['user_id'])

        Friends.objects.filter(Q(
            sender=sender, receiver=receiver, 
            application_status = 'pending')|
            Q(sender=sender, receiver = receiver, 
              application_status = 'rejected')).delete()
        
        return JsonResponse({'status': 'ok'})
            
class FriendReject(LoginRequiredMixin, View):

    """Контроллр для отмены входящей заявки в друзья
    """
    def post(self, request):
        data = json.loads(request.body)
        
        sender = User.objects.get(id=data['user_id'])
        receiver = request.user

        Friends.objects.filter(
            sender=sender, receiver=receiver, 
            application_status = 'pending').delete()
        
        Friends.objects.create(
            sender=sender, receiver=receiver, 
            application_status = 'rejected')
        
        return JsonResponse({'status': 'ok'})


class FriendDelete(LoginRequiredMixin,View):

    """Контроллер для удаления друга
    """

    def post(self, request):
        data = json.loads(request.body)
        
        deleter = request.user 
        deleted = User.objects.get(id=data['friend_id'])

        Friends.objects.filter(
            Q(sender=deleter, receiver=deleted, 
              application_status = 'accepted')|
            Q(sender=deleted, receiver=deleter, 
              application_status = 'accepted')).delete()

        return JsonResponse({'status': 'ok'})
    


class FriendProfileView(LoginRequiredMixin, View):

    """Контроллер для отображения профиля другого пользователя
    """ 

    def get(self, request, **kwargs):
        friend = User.objects.get(id = kwargs['id'])

        publications = Publications.objects.filter(user = kwargs['id'])
        
        context = {
            'title': 'Профиль',
            'publications': publications,
            'friend':friend,
            }
        
        if friend == request.user:
            context['me_user'] = True
        else:
            context['is_friend_profile'] = True

        return render(request, 'profile.html', context)



