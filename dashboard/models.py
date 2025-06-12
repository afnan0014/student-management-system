from django.db import models
from accounts.models import StudentProfile, StaffProfile
from courses.models import Course
from attendance.models import Attendance
from exams.models import Mark, Exam

class DashboardMetrics(models.Model):
    total_students = models.IntegerField(default=0)
    total_staff = models.IntegerField(default=0)
    active_courses = models.IntegerField(default=0)
    avg_attendance_rate = models.FloatField(default=0.0)
    avg_exam_scores = models.FloatField(default=0.0)

    def __str__(self):
        return "Dashboard Metrics Overview"
