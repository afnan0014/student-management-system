from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Course(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    class Meta:
        ordering = ['department', 'name']

class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    semester = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Semester must be at least 1."),
            MaxValueValidator(10, message="Semester cannot be greater than 10.")
        ]
    )
    staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'Staff'},
        related_name='subjects'
    )

    def __str__(self):
        staff_info = f" - Staff: {self.staff.username}" if self.staff else ""
        return f"{self.name} - Sem {self.semester} ({self.course.name}){staff_info}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.staff:
            from accounts.models import StaffProfile
            staff_profile, created = StaffProfile.objects.get_or_create(user=self.staff)
            # Only update department and course if they are not already set
            if created or not staff_profile.department:
                staff_profile.department = self.course.department
            if created or not staff_profile.course:
                staff_profile.course = self.course
            staff_profile.save()

    class Meta:
        ordering = ['course', 'semester', 'name']