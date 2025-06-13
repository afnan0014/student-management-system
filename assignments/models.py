from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import Course, Subject

# ---------------------------------------
# Assignment Resources
# ---------------------------------------

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

# ---------------------------------------
# Assignment Main Model
# ---------------------------------------

class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('individual', 'Individual Work'),
        ('group', 'Group Work'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='assignments')
    semester = models.IntegerField()
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_created')
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='individual')
    deadline = models.DateTimeField()

    # Optional direct content
    text_content = models.TextField(blank=True, null=True)
    link_content = models.URLField(blank=True, null=True)
    file_content = models.FileField(upload_to='assignments/files/', blank=True, null=True)
    image_content = models.ImageField(upload_to='assignments/images/', blank=True, null=True)

    # Related users
    students = models.ManyToManyField(User, related_name='assigned_work', blank=True)

    # Resource attachments
    files = models.ManyToManyField(AssignmentFile, blank=True, related_name='assignment_files')
    images = models.ManyToManyField(AssignmentImage, blank=True, related_name='assignment_images')
    links = models.ManyToManyField(AssignmentLink, blank=True, related_name='assignment_links')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ---------------------------------------
# Submission Resources
# ---------------------------------------

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

# ---------------------------------------
# Submission Model
# ---------------------------------------

class Submission(models.Model):
    SUBMISSION_STATUSES = [
        ('pending', 'Pending'),
        ('on_time', 'On Time'),
        ('late', 'Late'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission content
    text_submission = models.TextField(blank=True, null=True)
    file_submission = models.FileField(upload_to='submissions/files/', blank=True, null=True)
    image_submission = models.ImageField(upload_to='submissions/images/', blank=True, null=True)

    # Attachments
    files = models.ManyToManyField(SubmissionFile, blank=True, related_name='submission_files')
    images = models.ManyToManyField(SubmissionImage, blank=True, related_name='submission_images')

    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUSES, default='pending')

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"
