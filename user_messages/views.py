"""
    Контроллер приложения user_messages

    UserMessagesView - Контроллер для отображения диалогов пользователя
    UserMessageView - Контроллер для отображения конкретного диалога

"""
from django.shortcuts import render
from django.db.models import Q
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from user_messages.models import Messages
from django.views.generic import CreateView
from user_messages.forms import MessageForm
from users.models import User

class UserMessagesView(LoginRequiredMixin, View):

    """Контроллер для отображения диалогов пользователя"""
    
    def get(self,request):
        """Возвращает шаблон с пользователями с которыми диалог у текущего 
           пользователя"""
        users_messages = Messages.objects.filter(
            Q(sender=request.user)|Q(recipient=request.user)
            ).select_related('sender','recipient').order_by('-timestamp')

        users = [] 
        for user_message in users_messages:
            if user_message.sender not in users:
                users.append(user_message.sender)
            if user_message.recipient not in users:
                users.append(user_message.recipient)

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

        users_messages = Messages.objects.filter(
            Q(sender=self.request.user)|Q(recipient=self.request.user)
            ).select_related('sender','recipient').order_by('-timestamp')

        users = [] 
        for user_message in users_messages:
            if user_message.sender not in users:
                users.append(user_message.sender)
            if user_message.recipient not in users:
                users.append(user_message.recipient)

        personal_messages = users_messages.filter(
            Q(sender = self.kwargs['user_id'], recipient = self.request.user)|
            Q(sender = self.request.user, recipient = self.kwargs['user_id'])).order_by('timestamp')

        context['users'] = users
        context['chat_user'] = True # Активирует icnlude 
        context['personal_messages'] = personal_messages
        context['dialog_user'] = User.objects.get(id = self.kwargs['user_id']) # Будет ли ошибка если пользователь удалится? 
        return context
      
      def form_valid(self, form):
          form.instance.sender = self.request.user
          form.instance.recipient = User.objects.get(id = self.kwargs['user_id'])
          return super().form_valid(form)
      
      def get_success_url(self):
        return self.request.path
      
        

