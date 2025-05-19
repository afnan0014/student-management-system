from django import forms
from django.contrib.auth.models import User, Group

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[
        ('Student', 'Student'),
        ('Staff', 'Staff'),
        ('Admin', 'Admin'),
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
