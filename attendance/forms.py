from django import forms
from django.contrib.auth.models import User
from attendance.models import Attendance
from django.forms import modelformset_factory

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status']


AttendanceFormSet = modelformset_factory(
    Attendance,
    form=AttendanceForm,
    extra=0
)
