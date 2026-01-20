from django import forms
from publications.models import Publications

class UserRegisterForm(forms.ModelForm):
    """Форма для создания публикации"""

    class Meta:
        model = Publications
        fields = [
            'user','text',
            'media','topic',   
            ]

    