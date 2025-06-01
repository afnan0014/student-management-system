from django import forms
from .models import Mark
from .models import Exam
from courses.models import Course

from django import forms
from .models import Mark

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['marks_obtained']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'course', 'semester', 'date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }