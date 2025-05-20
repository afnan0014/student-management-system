from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
        })
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })
    )

    role = forms.ChoiceField(
        choices=[
            ('Student', 'Student'),
            ('Staff', 'Staff'),
            ('Admin', 'Admin'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select bg-secondary text-light border-0',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter email'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
