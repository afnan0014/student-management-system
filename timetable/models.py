from django.db import models
from courses.models import Course, Subject
from accounts.models import StaffProfile

class TimetableEntry(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    period_number = models.PositiveIntegerField(help_text="Period number in the day")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('course', 'semester', 'day', 'period_number')

    def __str__(self):
        return f"{self.course.name} - Sem {self.semester} - {self.day} P{self.period_number}"

class Holiday(models.Model):
    date = models.DateField(unique=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.date} - {self.title}"