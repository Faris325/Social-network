"""Модуль с контроллерами для приложения users

   UserLoginView - Контроллер для авторизации 
   UserRegistrationView - Контроллер для регистрации
   UserProfileView - Контроллер для отображения профиля 
   UserLogoutView - Контроллер для выхода из системы
   UserChangePassword - Контроллеры для изменения пароля
   UserChangeData - Контроллер для изменения данных пользователя
   UserFriends Контроллер для отображения профилей

"""

from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import auth
from django.views import View
from django.views.generic import CreateView
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.contrib.auth.views import LogoutView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchQuery

from users.forms import UserLoginForm
from users.forms import UserRegisterForm
from users.forms import ProfileChangeForm
from users.models import User
from friends.models import Friends
from publications.models import Publications


class UserLoginView(FormView):

    """Контроллер для формы авторизации"""

    template_name = 'authorization.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('users:profile') # reverse_lazy — это функция, которая используется для получения URL по имени маршрута, но делает это не немедленно, а "лениво", то есть только тогда, когда он будет использоваться, например, при перенаправлении.

    def get(self, request, *args, **kwargs):
        """Зарегистрированный пользователь перенаправляется на профиль"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
        
    def form_valid(self,form):
        """Возвращает объект модели и авторизует пользователя

         1. authenticate - это функция, которая пытается найти пользователя по
            переданным учетным записям(Возвращает объект модели или None)
         2. Метод .check_password проверяет введенный пароль с тем что в 
         объекте модели User
         3. Если был отправлен get параметр next, то будет перенаправление куда
            указывает next
         4. Метод .add_error добавляет к форме ошибку, если указать None, 
         значит что не относится к конретному полю, а получить 
         эту ошибку можно будет с помощью form.non_field_errors.

        """
        phone_number = form.cleaned_data['phone_number']
        password = form.cleaned_data['password']

        user = auth.authenticate(phone_number=phone_number, password=password)

        if user: 
            auth.login(self.request, user)

            next_url = self.request.GET.get('next')

            user_region = self.request.POST.get('timezone')
            if user_region:
                user.time_zone = user_region
                user.save()

            if next_url:
                HttpResponseRedirect(next)

            return super().form_valid(form)
        
        form.add_error(None, "Неверный номер телефона или пароль")
        return self.form_invalid(form)


class UserRegistrationView(CreateView):

    """Контроллер регистрации"""

    template_name = 'registration.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:profile')
  
    def form_valid(self, form):
        """Регистрирует клиента и перенаправляет на профиль

           1. Сохраняет пользователя в бд
           2. Обновляет сессию и передает новый куки клиенту
             
        """      
        user = form.save()
        auth.login(self.request, user)

        user_region = self.request.POST.get('timezone')
        if user_region:
            user.time_zone = user_region
            user.save()

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Регистрация'
        return context
    

class UserProfileView(LoginRequiredMixin, View):

    """Контроллер для отображения профиля""" 

    def get(self, request):
        publications = (Publications.objects.filter(user = request.user)
                        .order_by('-created_at'))
        
        context = {
            'title': 'Профиль',
            'publications': publications,
            'my_user': True
            }
        return render(request, 'profile.html', context)

     
class UserLogoutView(LoginRequiredMixin, LogoutView):
    
    """Контроллер для выхода пользователя из системы

       Выход из системы осуществляется через метод POST (для безопасности). 
       Если выход происходит на ту же страницу, метод POST вызовет GET, 
       который вернет шаблон с контекстом.
    
    """
    
    next_page = reverse_lazy('users:login')


class UserChangePassword(LoginRequiredMixin, PasswordChangeView):

    """Контроллер для изменения пароля клиента"""

    template_name = 'profile.html'
    #form_class = PasswordChangeForm(дефолт)
    success_url = reverse_lazy('users:profile')


class UserChangeData(LoginRequiredMixin, UpdateView):

    """Контроллер для изменения данных пользователя """

    model = User
    template_name = 'profile.html'
    form_class = ProfileChangeForm
    success_url = reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        """Добавит в объект контроллера атрибут object c объектом модели 

           По умолчанию оно добавляет по slug, после передает этот объект в 
           instance объекта формы

        """    
        return self.request.user
    
    def form_valid(self, form):
        """ Удаление фотографии пользователя

            image - это объект, у него есть метод delete, который при вызове
            удаляет изображение из хранилища, а в базе данных остается пустое 
            значение.
        """
        if self.request.POST.get('DeleteImage'):
            profile = form.instance
            profile.image.delete()


        return super().form_valid(form)


class Users(LoginRequiredMixin, ListView):

    """Контроллер для отображения профилей

       Имеет следующие атрибуты: 
       context_object_name - дополнительно название контекста в контексте;
       template_name - шаблон;
       paginate_by - на странице будет выводиться 10 объектов.
       
       Методы 
       get_queryset - Возвращает всех пользователей, кроме текущего.
       get_context_data - добавляет допополнительное аргументы в кварисет,
       такие как - пользователи, которых текущий пользователь добавил в друзья
       и пользователи которым была отправлена заявка

    """


    context_object_name = 'qury_users'
    template_name = 'users.html'
    paginate_by = 10

    def get_context_data(self,*, object_list = None, **kwargs):
        """ Добавление дополнительных аргументов для контекста 

           Создается 2 списка, которые будут переданы в шаблон. 
           sent_friends - пользователи, которым была отправлена заявка в друзья
           add_friends - пользователи, которые в друзьях

           Создаются 2 кварисета
           sent_friends_query - кварисет пользователей, которым была отправлена
           заявка и она в статусе pending
           friends_query - кварисет друзей пользователя 

           Перебираются все пользователи, кроме текущего, если полльзователь
           есть в кварисете sent_friends_query, то объект добавляется в список
           sent_friends, если пользователь находится в кварисете friends_query
           то он добавится в список  add_friends.

           Эти списки будут использованы в шаблоне следующим образом: 
           Например если выводимый пользователь есть в списке sent_freiends, то
           будет надпись "отпарвлена заявка" 
        """
        sent_friends = []
        add_friends = []

        sent_friends_query = list(Friends.objects.filter(
            sender=self.request.user, application_status = 'pending'
            ))
        
        friends_query = list(Friends.objects.filter(
            Q(sender=self.request.user, application_status = 'accepted')
            |Q(receiver=self.request.user, application_status = 'accepted'))
            )
        
        friends = self.object_list
        for user in friends:
            if user in sent_friends_query:
                sent_friends.append(user)
            elif user in friends_query:
                add_friends.append(user)

        kwargs['sent_friends'] = sent_friends
        kwargs['add_friends'] = add_friends

        return super().get_context_data(**kwargs)
     
    def get_queryset(self):
        """ Метод для получениия кварисета пользователей 

            Если пользователь использоваль использовал поиск, то отправлет get 
            параметр  q , в котором значение для поиска, если оно есть, то
            будет произведен поолнтекстовый поиск с помощь SearchVector, а если 
            по пользователь ввел например часть имени будет произведен поиск 
            с помощью фильтра __icontains, который по имени и фамилии ищет 
            входит ли не полностью введеноое имя в какое то поле объекта.
        """
        q = self.request.GET.get('q')

        if q: 
            q = q.strip()

            search_query = User.objects.annotate(
                search = SearchVector("first_name", "last_name")).filter(Q(
                    search=SearchQuery(q))|
                    Q(first_name__icontains = q)|
                    Q(last_name__icontains = q)
                    ).exclude(id=self.request.user.id)
                    

            return search_query

        return User.objects.exclude(id=self.request.user.id)
        
        

