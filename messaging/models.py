from django.db import models
from accounts.models import CustomUser
from django.utils.translation import gettext_lazy as _

class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.title or f"Conversation {self.id}"
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['created_at']
    
    def mark_as_read(self):
        self.is_read = True
        self.save()

class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ChatBotQuery(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chatbot_queries')
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Query from {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name_plural = 'ChatBot Queries'
        ordering = ['-created_at']

class Appointment(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    RESCHEDULED = 'rescheduled'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (CONFIRMED, _('Confirmed')),
        (RESCHEDULED, _('Rescheduled')),
        (CANCELLED, _('Cancelled')),
        (COMPLETED, _('Completed')),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_appointments', limit_choices_to={'role': 'student'})
    consultant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='consultant_appointments', limit_choices_to={'role': 'consultant'})
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    meeting_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.student.username} with {self.consultant.username} on {self.date}"
    
    class Meta:
        ordering = ['date', 'start_time']
