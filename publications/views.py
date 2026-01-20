"""
Модуль с контроллерами приложения publications

PublicationView - контроллер для отображения и создания публикаций
PublicationDelete - контроллер для удаления публикаций
PublicationLike - контроллер для лайка публикаций 
PublicationComments - контроллер для отображения публикаций
PublicationsTopic - контроллер для вывда публикаций по темам
PublicationTopicSearch - контроллер для поиска тем
"""
import json
from multiprocessing import context

from django.db.models import IntegerField 
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.db.models import Case 
from django.db.models import When
from django.db.models import F
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.template.loader import render_to_string
from django.db.models import Count
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchRank

from publications.forms import UserRegisterForm
from publications.models import Publications
from publications.models import Comments
from friends.models import Friends


class PublicationsView(LoginRequiredMixin, CreateView):
    """Контроллер для отображения и создания публикаций""" 
    
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
        """Добавляет в контекст публикации пользователя и его друзей.

        1. Получает список id друзей 
           пользователя.
        2. Получает публикации которые относятся к этим id 
        3. Добавляет публикации в контекст для отображения в шаблоне.
        """

        context = super().get_context_data(**kwargs)
    
        friends_id = list(Friends.objects.filter(
            Q(sender=self.request.user, application_status='accepted')|
            Q(receiver=self.request.user, application_status='accepted')
            ).annotate(friend_id = Case(
                When(sender=self.request.user, then=F('receiver_id')),
                When(receiver=self.request.user, then=F('sender_id')),
                output_field=IntegerField()
            )
            ).values_list('friend_id', flat=True)
        )


        firends_publication = (Publications.objects.filter(user__in=friends_id)
                        .select_related("user").order_by('-created_at')
                        )
        
        context['friends_publications'] = firends_publication 


        context['popular_publications'] = (Publications.objects.
                                annotate(likes=Count('liked_by'))
                                .order_by('-likes'))

        context['topics'] = (Publications.objects
                             .values_list('topic',flat=True)
                             .order_by('-created_at'))

        return context


class PublicationDelete(View):
    """Контроллер для удаления публикации"""

    def post(self, request):
        data = json.loads(request.body)
        
        Publications.objects.get(id=data['publication_id']).delete()

        return JsonResponse({'status': 'ok'})


class PublicationLike(View):
    """Контроллер для лайка к публикациям """

    def post(self,request):
        data = json.loads(request.body)
        publication = Publications.objects.get(id = data['publication_id'])

        if not publication.liked_by.filter(id = request.user.id).exists():
            publication.liked_by.add(request.user)
            return JsonResponse({'status': 'ok'})
        else:
            publication.liked_by.remove(request.user)
            return JsonResponse({'status': 'not_ok'})
        

class PublicationComments(View):
    """Контроллер для отображения комметариев"""

    def get(self,request):
        data = request.GET.get('publication_id')
        publication = Publications.objects.get(id = data)

        publication_comments = (publication.comments.all()
                                .select_related('user').order_by('created_at'))

        context = {
            'publication':publication,
            'comments':publication_comments
            }       

        html = render_to_string(
            'includes/comments-publication.html', context, request)

        return JsonResponse({'html': html})

    def post(self, request):
        data = json.loads(request.body)

        publication = Publications.objects.get(id=data['publication_id'])

        Comments.objects.create(publication=publication, text=data['text'], 
                                user=request.user
                                )

        return JsonResponse({'status': 'ok'})
    

class PublicationTopic(View):
    """Для вывода публикаций по темам"""

    def get(self,request, **kwargs):
        
        topic_publications = (Publications.objects.
                              filter(topic=self.kwargs['topic']))

        context = {
            'topic_publications': topic_publications
        }
        return render(request, "topic.html", context)
    
class PublicationTopicSearch(View):
    """Контроллер для поиска тем"""

    def get(self,request, **kwargs):
        
        search_topic = SearchQuery(request.GET.get('q'))
        search_query = (Publications.objects.annotate(
            search=SearchVector("text","topic",config="simple"),
            rank=SearchRank(SearchVector("text","topic"),search_topic))
            .filter(search=search_topic).order_by('-rank'))

        topics = search_query.values_list('topic',flat=True)

        friends_id = list(Friends.objects.filter(
            Q(sender=self.request.user, application_status='accepted')|
            Q(receiver=self.request.user, application_status='accepted')
            ).annotate(friend_id = Case(
                When(sender=self.request.user, then=F('receiver_id')),
                When(receiver=self.request.user, then=F('sender_id')),
                output_field=IntegerField()
            )
            ).values_list('friend_id', flat=True))


        firends_publication = (Publications.objects.filter(user__in=friends_id)
                        .select_related("user").order_by('-created_at')
                        )
        
        popular_publications = (Publications.objects.
                                annotate(likes=Count('liked_by'))
                                .order_by('-likes'))

        context = {
            'topics': topics,
            'firends_publication':firends_publication,
            'popular_publications':popular_publications, 
            'topics_tab_active':True,
        }

        return render(request, "publications.html", context)