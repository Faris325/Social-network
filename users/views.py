"""Модуль с контроллерами для приложения users

   UserLoginView - Контроллер для авторизации 
   UserRegistrationView - Контроллер для регистрации
   UserProfileView - Контроллер для отображения профиля 
   UserLogoutView - Контроллер для выхода из системы
   UserChangePassword - Контроллеры для изменения пароля
   UserChangeData - Контроллер для изменения данных пользователя
   UserFriends Контроллер для отображения профилей

"""

from multiprocessing import AuthenticationError
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

from users.forms import UserLoginForm
from users.forms import UserRegisterForm
from users.forms import ProfileChangeForm
from users.models import User



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

        return HttpResponseRedirect(self.success_url) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Регистрация'
        return context
    

class UserProfileView(LoginRequiredMixin, View):

    """Контроллер для отображения профиля""" 

    def get(self, request):
        context = {
            'title': 'Профиль'
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
        
        if self.request.POST.get('DeleteImage'):
            profile = form.instance
            profile.image.delete()


        return super().form_valid(form)

class UserFriends(LoginRequiredMixin, ListView):

    """Контроллер для отображения профилей

       Имеет следующие атрибуты: 
       context_object_name - дополнительно название контекста в контексте;
       template_name - шаблон;
       paginate_by - на странице будет выводиться 10 объектов.
       
       Методы 
       get_queryset - Возвращает всех пользователей, кроме текущего.

    """


    context_object_name = 'qury_users'
    template_name = 'users.html'
    paginate_by = 10

    
    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)
        
        


