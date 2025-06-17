import json

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from publications.forms import UserRegisterForm
from publications.models import Publications
from friends.models import Friends

class PublicationsView(LoginRequiredMixin, CreateView):

    """Контроллер для отображения и создания публикаций
    """ 
    
    form_class = UserRegisterForm
    template_name = 'publications.html'
    success_url = reverse_lazy('publications:publication')

    def form_valid(self, form):
        """Метод для валидации объекта формы

           Добавляет в атрибут объекта instance объект модели user, чтобы
           в бд сохранилось id пользователя который сделал публикацию. 
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Метод контекста

           Дополнительно добавляет публикации друзей в контекст 

           В начале получаем кварисет объектов Friends с текущим пользователей,
           которая хранит с кем пользователь является в друзьях.
           Создается пустой список, который будет хранить id друзей и id 
           текущего пользователя(чтобы и его посты были видны в ленте).
           Далее происходит перебор кварисета friends и в friends_id попадают 
           id друзей текущего пользователя.
           Далее получаем кварисет публикаций всех пользователей, создаем 
           список публикаций друзей.
           Перебираем кварисет публикаций, если публикацию делал друг
           пользователя, добавляем ее в список публикаций. 
           По итогу в шаблоне будут выведены публикации только друзей.
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

        context['publications'] = friends_publications
        return context
    

class PublicationDelete(LoginRequiredMixin, View):

    """Контроллер для удаления публикации
    """

    def post(self, request):
        data = json.loads(request.body)
        
        Publications.objects.get(id=data['publication_id']).delete()

        return JsonResponse({'status': 'ok'})
