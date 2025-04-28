
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
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

    email = forms.CharField(required=False)
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 
            'phone_number','email'

            ]  
        error_messages = {
            'phone_number': {
                'max_length': 'Номер телефона не должен превышать 15 '
                'символов.',
                'required': 'Это поле обязательно для заполнения',
                'unique': 'Пользователь с таким номером телефона уже '
                'существует.',
            },
            'first_name':{
                'max_length': 'Имя не должно превышать 150 символов.',
                'min_length': 'Имя не должно быть меньше 3 символов.',
                'required': 'Это поле обязательно для заполнения',

            },
            'last_name' : {
                'max_length': 'Фамилия не должна превышать 150 символов.',
                'min_length': 'Фамилия не должна быть меньше 3 символов.',
                'required': 'Это поле обязательно для заполнения',
            },
            'email': {
                'max_length': 'Email не должен превышать 150 символов.',
                'required': 'Это поле обязательно для заполнения',
                'min_length': 'Email не должен быть меньше 3 символов.',
            },

        }

        

class ProfileChangeForm(forms.ModelForm):

    """Форма для изменения данных клиента

       Если поля переопределены в теле формы, их необходимо указать в 'fields',
       так как при переопределении полей они не связаны с моделью. Следовательно, 
       если они не указаны в 'fields', они не будут сохраняться автоматически 
       в модели при вызове save().

    """
    last_name = forms.CharField(max_length=150, required=False)
    first_name = forms.CharField(max_length=150, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    email = forms.CharField(max_length=15, required=False)
    class Meta:
        model = User
        fields = [
            'last_name', 'first_name', 'phone_number',
            'email', 'image',
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
        cleaned_data['first_name'] = (cleaned_data.get('first_name') 
                                      or user.first_name
                                      )
        cleaned_data['last_name'] = (cleaned_data.get('last_name') 
                                     or user.last_name
                                     )
        cleaned_data['phone_number'] = (cleaned_data.get('phone_number') 
                                        or user.phone_number
                                        )
        cleaned_data['email'] = (cleaned_data.get('email') 
                                 or user.email
                                 )
        
        # Объединение email и emailProvider
        # email_provider = cleaned_data.get('emailProvider')
        # if cleaned_data['email'] and email_provider:
        #     cleaned_data['email'] = f"{cleaned_data['email']}@{email_provider}"
        return cleaned_data
    



