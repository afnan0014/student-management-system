from django.db import models
from django.contrib.auth.models import User
from courses.models import Course

class Message(models.Model):
    MESSAGE_TYPES = (
        ('all', 'All'),
        ('staff_only', 'Staff Only'),
        ('students_only', 'Students Only'),
        ('personal', 'Personal'),
        ('group', 'Group'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='personal')
    timestamp = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    is_announcement = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"

class MessageAttachment(models.Model):
    ATTACHMENT_TYPE_CHOICES = (
        ('link', 'Link'),
        ('file', 'File'),
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES)
    link = models.URLField(max_length=500, null=True, blank=True)
    file = models.FileField(upload_to='message_attachments/', null=True, blank=True)

    def __str__(self):
        if self.attachment_type == 'link':
            return f"Link: {self.link}"
        return f"File: {self.file.name if self.file else 'No file'}"

class MessageRecipient(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='recipients')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    is_read = models.BooleanField(default=False)
    read_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('message', 'recipient')

    def __str__(self):
        return f"{self.recipient} received {self.message}"