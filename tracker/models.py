from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProgressUpdate(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    # Links back to the Main Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    # Links to the developer who wrote it
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updates')
    task_done = models.CharField(max_length=255, verbose_name="What are you working on?")
    details = models.TextField(verbose_name="Detailed Progress Log")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Permission Flag: Allows the superuser to lock editing down at will
    can_edit = models.BooleanField(default=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} -> {self.project.title}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='direct_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Track who has clicked "Read/Acknowledged"
    acknowledged_by = models.ManyToManyField(User, blank=True, related_name='acknowledged_alerts')

    def __str__(self):
        return f"Broadcast to All" if not self.recipient else f"Direct to {self.recipient.username}"

    def __str__(self):
        return f"Broadcast to All" if not self.recipient else f"Direct to {self.recipient.username}"