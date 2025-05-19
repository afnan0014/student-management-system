from django import forms
from .models import Department, Course, Subject
from django.contrib.auth.models import User

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'department']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'course', 'semester', 'staff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only Staff users in staff dropdown
        self.fields['staff'].queryset = User.objects.filter(groups__name='Staff')
