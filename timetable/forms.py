from django import forms
from .models import TimetableEntry, Holiday

class TimetableForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = '__all__'

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = '__all__'
