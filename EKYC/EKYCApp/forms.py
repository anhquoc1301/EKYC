from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model =User
        fields = ['fullname', 'address', 'birthday', 'card_number']