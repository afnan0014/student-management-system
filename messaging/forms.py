from django import forms
from django.contrib.auth.models import User
from courses.models import Course
from accounts.models import StaffProfile, StudentProfile
from .models import Message

class MessageForm(forms.ModelForm):
    message_type = forms.ChoiceField(
        choices=[
            ('all', 'All (Staff and Students)'),
            ('staff_only', 'Staff Only'),
            ('students_only', 'Students Only'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    staff_message_type = forms.ChoiceField(
        choices=[
            ('personal', 'Personal'),
            ('group', 'Group'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), label="Message Content")
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Message
        fields = ['content', 'course', 'semester']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            semester_choices = StudentProfile.objects.values_list('semester', flat=True).distinct().order_by('semester')
            self.fields['semester'].choices = [('', 'Select Semester')] + [(sem, f"Semester {sem}") for sem in semester_choices]

            if self.user.is_superuser:
                self.fields['course'].queryset = Course.objects.all()
            elif self.user.groups.filter(name='Staff').exists():
                try:
                    staff_profile = StaffProfile.objects.get(user=self.user)
                    if staff_profile.course:
                        self.fields['course'].queryset = Course.objects.filter(id=staff_profile.course.id)
                        semesters = StudentProfile.objects.filter(course=staff_profile.course).values_list('semester', flat=True).distinct().order_by('semester')
                        self.fields['semester'].choices = [('', 'Select Semester')] + [(sem, f"Semester {sem}") for sem in semesters]
                    else:
                        self.fields['course'].queryset = Course.objects.none()
                        self.fields['semester'].choices = [('', 'Select Semester')]
                except StaffProfile.DoesNotExist:
                    self.fields['course'].queryset = Course.objects.none()
                    self.fields['semester'].choices = [('', 'Select Semester')]
            elif self.user.groups.filter(name='Student').exists():
                try:
                    student_profile = StudentProfile.objects.get(user=self.user)
                    if student_profile.course:
                        self.fields['course'].queryset = Course.objects.filter(id=student_profile.course.id)
                        semesters = StudentProfile.objects.filter(course=student_profile.course).values_list('semester', flat=True).distinct().order_by('semester')
                        self.fields['semester'].choices = [('', 'Select Semester')] + [(sem, f"Semester {sem}") for sem in semesters]
                    else:
                        self.fields['course'].queryset = Course.objects.none()
                        self.fields['semester'].choices = [('', 'Select Semester')]
                except StudentProfile.DoesNotExist:
                    self.fields['course'].queryset = Course.objects.none()
                    self.fields['semester'].choices = [('', 'Select Semester')]

            if self.user.groups.filter(name='Staff').exists():
                try:
                    staff_profile = StaffProfile.objects.get(user=self.user)
                    if staff_profile.course:
                        student_profiles = StudentProfile.objects.filter(course=staff_profile.course)
                        self.fields['recipient'].queryset = User.objects.filter(
                            groups__name='Student',
                            student_profile__in=student_profiles
                        ).distinct()
                    else:
                        self.fields['recipient'].queryset = User.objects.none()
                except StaffProfile.DoesNotExist:
                    self.fields['recipient'].queryset = User.objects.none()
            elif self.user.groups.filter(name='Student').exists():
                self.fields.pop('staff_message_type')
                try:
                    student_profile = StudentProfile.objects.get(user=self.user)
                    if student_profile.course:
                        staff_profiles = StaffProfile.objects.filter(course=student_profile.course)
                        self.fields['recipient'].queryset = User.objects.filter(
                            groups__name='Staff',
                            staff_profile__in=staff_profiles
                        ).distinct()
                    else:
                        self.fields['recipient'].queryset = User.objects.none()
                except StudentProfile.DoesNotExist:
                    self.fields['recipient'].queryset = User.objects.none()
            if self.user.is_superuser:
                self.fields.pop('staff_message_type')
                self.fields.pop('recipient')
            else:
                self.fields.pop('message_type')

    def save(self, commit=True, sender=None):
        instance = super().save(commit=False)
        if sender is not None:
            instance.sender = sender
        if self.user.is_superuser:
            instance.message_type = self.cleaned_data['message_type']
        elif self.user.groups.filter(name='Staff').exists():
            instance.message_type = self.cleaned_data['staff_message_type']
        else:
            instance.message_type = 'personal'
        instance.semester = int(self.cleaned_data['semester']) if self.cleaned_data['semester'] else None
        if commit:
            instance.save()
        return instance