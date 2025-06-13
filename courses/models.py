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
    semester = models.IntegerField(default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'Staff'},
        related_name='assigned_courses'
    )

    def __str__(self):
        staff_info = f" - {self.assigned_staff.username}" if self.assigned_staff else ""
        return f"{self.name} (Sem {self.semester}){staff_info}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.assigned_staff:
            from accounts.models import StaffProfile
            staff_profile, created = StaffProfile.objects.get_or_create(user=self.assigned_staff)
            if created or not staff_profile.department:
                staff_profile.department = self.department
            if created or not staff_profile.course:
                staff_profile.course = self
            staff_profile.save()

    class Meta:
        ordering = ['department', 'semester', 'name']


class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return self.name