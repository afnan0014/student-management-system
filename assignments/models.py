from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Subject
from django.utils import timezone

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='assignments')
    semester = models.IntegerField()
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_created')
    assignment_type = models.CharField(max_length=20, choices=[
        ('individual', 'Individual Work'),
        ('group', 'Group Work'),
    ], default='individual')  # New field to track assignment type
    deadline = models.DateTimeField()
    text_content = models.TextField(blank=True, null=True)
    link_content = models.URLField(blank=True, null=True)
    file_content = models.FileField(upload_to='assignments/files/', blank=True, null=True)
    image_content = models.ImageField(upload_to='assignments/images/', blank=True, null=True)
    students = models.ManyToManyField(User, related_name='assigned_work')
    created_at = models.DateTimeField(auto_now_add=True)

    # Add ManyToMany fields for multiple files, images, and links
    files = models.ManyToManyField('AssignmentFile', blank=True, related_name='assignment_files')
    images = models.ManyToManyField('AssignmentImage', blank=True, related_name='assignment_images')
    links = models.ManyToManyField('AssignmentLink', blank=True, related_name='assignment_links')

    def __str__(self):
        return self.title

class AssignmentFile(models.Model):
    file = models.FileField(upload_to='assignments/files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class AssignmentImage(models.Model):
    image = models.ImageField(upload_to='assignments/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name

class AssignmentLink(models.Model):
    url = models.URLField()
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    text_submission = models.TextField(blank=True, null=True)
    file_submission = models.FileField(upload_to='submissions/files/', blank=True, null=True)
    image_submission = models.ImageField(upload_to='submissions/images/', blank=True, null=True)
    files = models.ManyToManyField('SubmissionFile', blank=True, related_name='submission_files')
    images = models.ManyToManyField('SubmissionImage', blank=True, related_name='submission_images')
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('on_time', 'On Time'),
        ('late', 'Late'),
    ], default='pending')

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"

class SubmissionFile(models.Model):
    file = models.FileField(upload_to='submissions/files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class SubmissionImage(models.Model):
    image = models.ImageField(upload_to='submissions/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name