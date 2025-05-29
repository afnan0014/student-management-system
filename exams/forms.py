from django import forms
from .models import Mark

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'subject', 'marks_obtained']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

MarkFormSet = forms.modelformset_factory(
    Mark,
    form=MarkForm,
    extra=0,
    can_delete=False
)
