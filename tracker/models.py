from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    # --- ADD THIS FIELD TO TRACK STATUS ---
    is_completed = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} {'[COMPLETED]' if self.is_completed else '[ACTIVE]'}"
class ProgressUpdate(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updates')
    task_done = models.CharField(max_length=255)
    details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Advanced CRUD Permissions Grid Control matrix
    can_update = models.BooleanField(default=True, help_text="Designates whether the owner can modify this log.")
    can_delete = models.BooleanField(default=False, help_text="Designates whether the owner can purge this log.")

    def __str__(self):
        return f"{self.user.username} -> {self.project.title}"

class Notification(models.Model):
    # If recipient is null, it means it's a global group broadcast
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=models.DateTimeField(auto_now_add=True))

    def __str__(self):
        if self.recipient:
            return f"To @{self.recipient.username}: {self.message[:30]}"
        return f"Global Broadcast: {self.message[:30]}"