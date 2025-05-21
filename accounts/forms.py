from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Enter username'

        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password'
        })
