"""
    Контроллер приложения user_messages

    UserMessagesView - Контроллер для отображения диалогов пользователя
    UserMessageView - Контроллер для отображения конкретного диалога

"""
from django.shortcuts import render
from django.db.models import Q
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case
from django.db.models import When
from django.db.models import F
from django.db.models import Value

import user_messages
from user_messages.models import Messages
from django.views.generic import CreateView
from user_messages.forms import MessageForm
from users.models import User

class UserMessagesView(LoginRequiredMixin, View):

    """Контроллер для отображения диалогов пользователя"""
    
    def get(self,request):
        """Возвращает шаблон с пользователями с которыми диалог у текущего 
           пользователя"""
        dialog_users = (
            Messages.objects.filter(
            Q(sender=request.user)|Q(recipient=request.user))
            .select_related('sender','recipient')
            .order_by('-timestamp')
            .annotate(
            friend = Case(
                When(sender=request.user, then=F("recipient")),
                When(recipient=request.user, then=F("sender")),
                default=Value(None) 
            ))
            .values_list("friend",flat=True)
            )
        

        users = User.objects.filter(id__in=dialog_users)

        context = {
            'users':users 
        } 
        return render(request, 'messages.html', context)


class UserMessageView(LoginRequiredMixin, CreateView):
      
      """Добавляет в контекст данные о сообщениях пользователя:
      - список всех собеседников (sender или recipient),
      - сообщения между текущим пользователем и выбранным пользователем 
      (по user_id).
      """
      
      form_class = MessageForm
      template_name = 'messages.html'
      
      def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dialogs = (Messages.objects.filter(
            Q(sender=self.request.user)|Q(recipient=self.request.user))
            .select_related('sender','recipient')
            .order_by('-timestamp')
            )
        
        dialog_users = (dialogs.annotate(
            friend = Case(
                When(sender=self.request.user, then=F("recipient")),
                When(recipient=self.request.user, then=F("sender")),
                default=Value(None) 
            ))
            .values_list("friend",flat=True)
            )
        users = User.objects.filter(id__in=dialog_users)


        personal_messages = (dialogs.filter(
            Q(sender = self.kwargs['user_id'], recipient = self.request.user)|
            Q(sender = self.request.user, recipient = self.kwargs['user_id']))
            .order_by('timestamp')
            )
        

        context['users'] = users
        context['chat_user'] = True # Активирует icnlude с сообщениями
        context['personal_messages'] = personal_messages
        context['dialog_user'] = User.objects.get(id = self.kwargs['user_id']) # Будет ли ошибка если пользователь удалится? 
        return context
      
      def form_valid(self, form):
          form.instance.sender = self.request.user
          form.instance.recipient = User.objects.get(id = self.kwargs['user_id'])
          return super().form_valid(form)
      
      def get_success_url(self):
        return self.request.path
      
        

