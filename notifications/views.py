from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import ConsultantNotificationForm
from .models import Notification
from accounts.models import CustomUser

# Helper function (consider moving to a shared utils module)
def is_consultant(user):
    return user.is_authenticated and user.role == 'consultant'

@user_passes_test(is_consultant, login_url=reverse_lazy('accounts:login'))
def consultant_send_notification(request):
    """Allows consultants to send notifications to their assigned students."""
    consultant = request.user

    if request.method == 'POST':
        form = ConsultantNotificationForm(request.POST, consultant=consultant)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            message_content = form.cleaned_data['message']

            # Create the notification
            Notification.objects.create(
                recipient=recipient,
                sender=consultant, # Record who sent it
                message=message_content,
                notification_type='manual' # Add a type for manually sent messages
            )

            messages.success(request, f"Notification sent successfully to {recipient.get_full_name() or recipient.username}.")
            # Redirect back to the form or another relevant page (e.g., consultant dashboard)
            return redirect('dashboard:consultant_send_notification') # Redirect back to the same form page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ConsultantNotificationForm(consultant=consultant)

    context = {
        'form': form,
        'page_title': 'Send Notification to Student'
    }
    # Need to create this template: templates/notifications/consultant_send_notification.html
    return render(request, 'notifications/consultant_send_notification.html', context)

# Add other notification views if needed (e.g., list, detail, mark read - some might be in dashboard/views.py)
