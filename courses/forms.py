from django import forms
from django.forms import modelformset_factory
from .models import Department, Course, Subject
from django.contrib.auth.models import User

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-secondary text-light border-0'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'department', 'semester', 'assigned_staff']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter course name'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select bg-secondary text-light border-0'
            }),
            'semester': forms.NumberInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter semester',
                'min': 1,
                'max': 8
            }),
            'assigned_staff': forms.Select(attrs={
                'class': 'form-select bg-secondary text-light border-0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_staff'].queryset = User.objects.filter(groups__name='Staff')


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control bg-secondary text-light border-0',
                'placeholder': 'Enter subject name'
            }),
        }

# Subject formset for dynamic input fields
SubjectFormSet = modelformset_factory(
    Subject,
    form=SubjectForm,
    extra=1,
    can_delete=True
)
