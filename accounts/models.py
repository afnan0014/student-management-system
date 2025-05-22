from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Course, Department

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='students')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='students')
    batch_number = models.IntegerField(
        help_text="Enter the batch year (e.g., 2023).",
        validators=[
            MinValueValidator(2000, message="Batch year must be at least 2000."),
            MaxValueValidator(2030, message="Batch year cannot be greater than 2030.")
        ]
    )

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='staff')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='staff')

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"