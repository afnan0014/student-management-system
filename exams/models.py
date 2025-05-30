# exams/models.py

from django.db import models
from accounts.models import StudentProfile
from courses.models import Course, Subject

class Exam(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"{self.name} - Sem {self.semester}"

class Mark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.marks_obtained}"

class Result(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_marks = models.FloatField()
    grade = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.name} - {self.grade}"
