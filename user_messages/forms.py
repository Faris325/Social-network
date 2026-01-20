from django import forms
from user_messages.models import Messages

class MessageForm(forms.ModelForm):
    """Форма для отправки сообщений"""

    class Meta:
        model = Messages
        fields = [
            'sender','recipient',
            'content','media' 
            ]

