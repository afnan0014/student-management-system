from django.db import models
from courses.models import Course
from accounts.models import StudentProfile
from django.contrib.auth.models import User

# class Attendance(models.Model):
#     STATUS_CHOICES = [
#         ('Present', 'Present'),
#         ('Absent', 'Absent')
#     ]

#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
#     date = models.DateField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES)

#     class Meta:
#         unique_together = ('student', 'date', 'course')  

#     def __str__(self):
#         return f"{self.student.user.username} - {self.course.name} - {self.date} - {self.status}"
from accounts.models import StaffProfile

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),  # Added 'Late' to match previous context
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)  # Add staff reference

    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date', 'course')

    def __str__(self):
        return f"{self.student.user.username} - {self.course.name} - {self.date} - {self.status}"