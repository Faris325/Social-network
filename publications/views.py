"""
    Модуль с контроллерами приложения publications

    PublicationView - контроллер для отображения и создания публикаций
    PublicationDelete - контроллер для удаления публикаций
"""
import json

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from publications.forms import UserRegisterForm
from publications.models import Publications
from friends.models import Friends

class PublicationsView(LoginRequiredMixin, CreateView):

    """Контроллер для отображения и создания публикаций
    """ 
    
    form_class = UserRegisterForm
    template_name = 'publications.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        """Метод для валидации объекта формы

           Добавляет в атрибут объекта instance объект модели user, чтобы
           в бд сохранилось id пользователя который сделал публикацию. 
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Добавляет в контекст публикации пользователя и его друзей.

        1. Получает список друзей текущего пользователя.
        2. Формирует список ID друзей и самого пользователя.
        3. Фильтрует публикации, оставляя только те, что принадлежат этим ID.
        4. Добавляет их в контекст для отображения в шаблоне.
        """
        context = super().get_context_data(**kwargs)

        friends = Friends.objects.filter(
            Q(sender=self.request.user, application_status='accepted')|
            Q(receiver=self.request.user, application_status='accepted')
            ).select_related('sender', 'receiver')  
        friends_id = []
        friends_id.append(self.request.user.id)

        for friend in friends:
            if friend.sender == self.request.user:
                friends_id.append(friend.receiver.id)
            else:
                friends_id.append(friend.sender.id)

        users_publications = (Publications.objects.all()
                              .order_by('-created_at').select_related("user"))
        
        friends_publications = []

        for user_publication in users_publications:
            if user_publication.user.id in friends_id:
                friends_publications.append(user_publication)

        paginate_publications = Paginator(friends_publications, 6)
        if self.request.GET.get('page'):
            paginate_page = paginate_publications.page(self.request.GET.get('page'))
            publication_list = []
            for pub in paginate_page.object_list:
                publication_list.append({'id': pub.id,
                                         'text': pub.text,
                                         'created_at': pub.created_at,
                                         'user_id': pub.user_id,
                                         'media': pub.media 
                                         })
            return JsonResponse({'publications': publication_list})
        else:
             context['publications'] = paginate_publications.page(1)
        return context
    

class PublicationDelete(LoginRequiredMixin, View):

    """Контроллер для удаления публикации
    """

    def post(self, request):
        data = json.loads(request.body)
        
        Publications.objects.get(id=data['publication_id']).delete()

        return JsonResponse({'status': 'ok'})
