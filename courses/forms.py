from django import forms
from .models import Department, Course, Subject
from django.contrib.auth.models import User


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-secondary'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-secondary'}),
            'department': forms.Select(attrs={'class': 'form-select bg-secondary'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'course', 'semester', 'staff']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-secondary'}),
            'course': forms.Select(attrs={'class': 'form-select bg-secondary'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control bg-secondary', 'min': 1, 'max': 10}),
            'staff': forms.Select(attrs={'class': 'form-select bg-secondary'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only Staff users in staff dropdown
        self.fields['staff'].queryset = User.objects.filter(groups__name='Staff')