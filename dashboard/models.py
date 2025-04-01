from django.db import models
from accounts.models import CustomUser

class Analytics(models.Model):
    date = models.DateField(auto_now_add=True)
    total_students = models.PositiveIntegerField(default=0)
    total_consultants = models.PositiveIntegerField(default=0)
    total_applications = models.PositiveIntegerField(default=0)
    applications_accepted = models.PositiveIntegerField(default=0)
    applications_rejected = models.PositiveIntegerField(default=0)
    applications_processing = models.PositiveIntegerField(default=0)
    applications_submitted = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Analytics'
    
    def __str__(self):
        return f"Analytics for {self.date}"

class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

class DashboardNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dashboard_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} for {self.user.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
