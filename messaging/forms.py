from django import forms
from .models import Message, Attachment, Appointment
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class MessageForm(forms.ModelForm):
    """Form for creating and sending messages."""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Type your message here...',
                'class': 'form-control'
            }),
        }

class AttachmentForm(forms.Form):
    """Form for uploading message attachments."""

    attachments = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
            # Removed 'multiple': True
        })
    )

class ChatbotQueryForm(forms.Form):
    """Form for submitting queries to the chatbot."""
    
    query = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ask UniBot a question...',
            'class': 'form-control'
        })
    )

class AppointmentForm(forms.ModelForm):
    """Form for creating and editing appointments."""
    
    class Meta:
        model = Appointment
        fields = ['title', 'description', 'date', 'start_time', 'end_time', 'meeting_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Get current user to customize the form based on user role
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add student or consultant field based on user role
        if self.user:
            if self.user.role == 'student':
                self.fields['consultant'] = forms.ModelChoiceField(
                    queryset=CustomUser.objects.filter(role='consultant'),
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            elif self.user.role == 'consultant':
                self.fields['student'] = forms.ModelChoiceField(
                    queryset=CustomUser.objects.filter(role='student'),
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            elif self.user.is_staff:
                self.fields['student'] = forms.ModelChoiceField(
                    queryset=CustomUser.objects.filter(role='student'),
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
                self.fields['consultant'] = forms.ModelChoiceField(
                    queryset=CustomUser.objects.filter(role='consultant'),
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check that end time is after start time
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time.")
        
        # Check that date is not in the past
        if date and date < timezone.now().date():
            raise ValidationError("Cannot schedule appointments in the past.")
        
        return cleaned_data

class AdminReplyForm(forms.Form):
    """Form for admin replies within the Django admin interface."""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Type your reply here...',
            'class': 'vLargeTextField' # Use standard Django admin class
        }),
        label="Admin Reply"
    )
