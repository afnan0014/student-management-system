from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from courses.models import Course, Department

# -----------------------------
# User Creation Form (Admin Use)
# -----------------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Enter username',
            'autocomplete': 'username'
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


# -----------------------------
# Student Profile Form
# -----------------------------
class StudentProfileForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select bg-secondary text-light border-0'
        }),
        empty_label="Select a course"
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select bg-secondary text-light border-0'
        }),
        empty_label="Select a department"
    )

    batch_number = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-secondary text-light border-0',
            'placeholder': 'Enter batch year (e.g., 2023)',
            'min': 2000,
            'max': 2030
        }),
        help_text="Enter the batch year (e.g., 2023).",
        min_value=2000,
        max_value=2030
    )


# -----------------------------
# Staff Profile Form
# -----------------------------
class StaffProfileForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select bg-secondary text-light border-0'
        }),
        empty_label="Select a department",
        required=False  # Optional
    )

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select bg-secondary text-light border-0'
        }),
        empty_label="Select a course",
        required=False  # Optional
    )
