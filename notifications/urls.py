from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Add other notification-related URLs here if needed in the future
    # e.g., path('', views.notification_list, name='notification_list'),

    # Consultant Specific URL
    path('consultant/send/', views.consultant_send_notification, name='consultant_send_notification'),

    # Add the new view for sending consultant notifications
    path('send-consultant/', views.send_consultant_notification, name='send_consultant_notification'),
]
