
from django.contrib.auth.forms import UserCreationForm
from django import forms 


from users.models import User

class UserLoginForm(forms.Form):

    """Форма для авторизации пользователя"""

    phone_number = forms.CharField(
       max_length=15, 
       error_messages={
            'required':'Это поле обязательно для заполнения',
            'max_length':'Длина не должна превышать 15 символов'
            }
        )
    password = forms.CharField(
        error_messages={'required':'Это поле обязательно для заполнения'}
        )


class UserRegisterForm(UserCreationForm):

    """Форма для Регистрации пользователя

        Используются поля из модели User, где "username" заменен на 
        "phone_number". Для полей заданы сообщения об ошибках, которые будут 
        отображаться при некорректном вводе. Ошибки для паролей остаются 
        стандартными(язык сообщений ошибок зависит от настройки LANGUAGE_CODE).  

    """

    class Meta:
        model = User
        fields = [
            'nickname', 'phone_number',
            ]  
        error_messages = {
            'phone_number': {
                'max_length': 'Номер телефона не должен превышать 15 '
                'символов.',
                'required': 'Это поле обязательно для заполнения',
                'unique': 'Пользователь с таким номером телефона уже '
                'существует.',
            },
            'nickname':{
                'max_length': 'Имя не должно превышать 150 символов.',
                'min_length': 'Имя не должно быть меньше 3 символов.',
                'required': 'Это поле обязательно для заполнения',

            },

        }

        

class ProfileChangeForm(forms.ModelForm):

    """Форма для изменения данных клиента

       Если поля переопределены в теле формы, их необходимо указать в 'fields',
       так как при переопределении полей они не связаны с моделью. Следовательно, 
       если они не указаны в 'fields', они не будут сохраняться автоматически 
       в модели при вызове save().

    """
    nickname = forms.CharField(max_length=150, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    class Meta:
        model = User
        fields = [
            'nickname', 'phone_number',
            'image',
            ]

    def clean(self):
        """"Валидация формы и сохранение предыдущих значений полей.

            Если пользователь оставил поле пустым, в cleaned_data будет 
            подставлено его предыдущее значение из модели. 
        """
        cleaned_data = super().clean()
        # email = cleaned_data.get('email')
        # email_provider = cleaned_data.get('emailProvider')
        
        # if email and email_provider:
        #     cleaned_data['email'] = f"{email}@{email_provider}"

        user = self.instance
        
        # Если поле пустое, оставляем старое значение
        cleaned_data['nickname'] = (cleaned_data.get('nickname') 
                                      or user.nickname
                                      )

        cleaned_data['phone_number'] = (cleaned_data.get('phone_number') 
                                        or user.phone_number
                                        )
        # Объединение email и emailProvider
        # email_provider = cleaned_data.get('emailProvider')
        # if cleaned_data['email'] and email_provider:
        #     cleaned_data['email'] = f"{cleaned_data['email']}@{email_provider}"
        return cleaned_data
    



