from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter email'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter password',
                'autocomplete': 'new-password',
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Confirm password',
                'autocomplete': 'new-password',
            }),
        }