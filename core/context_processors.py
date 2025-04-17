from messaging.models import Message
from dashboard.models import DashboardNotification

def unread_counts(request):
    """
    Provides unread message and notification counts to the template context.
    """
    unread_messages_count = 0
    unread_notifications_count = 0

    if request.user.is_authenticated:
        # Count unread messages where the user is a participant but not the sender
        unread_messages_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        # Count unread dashboard notifications for the user
        unread_notifications_count = DashboardNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

    return {
        'unread_messages_count': unread_messages_count,
        'unread_notifications_count': unread_notifications_count,
    }
