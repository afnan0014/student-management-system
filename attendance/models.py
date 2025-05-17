from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from courses.models import Subject

class Attendance(models.Model):
    STATUS_CHOICES = [
          ('Present', 'Present'),
          ('Absent', 'Absent'),
          ('Leave', 'Leave'),
]
    date = models.DateField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE)
    limit_choices_to=({'groups__name': 'Student'})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    def __str__(self):
        return f"{self.date} - {self.subject.name} - {self.student.username} - {self.status}"
