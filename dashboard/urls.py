from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:user_id>/', views.student_detail, name='student_detail'),
    path('consultants/', views.consultant_list, name='consultant_list'),
    path('consultants/<int:user_id>/', views.consultant_detail, name='consultant_detail'),
    path('applications/', views.application_overview, name='application_overview'),
    path('analytics/', views.analytics, name='analytics'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('activities/', views.activity_log, name='activity_log'),
    path('search-universities/', views.university_search, name='university_search'), # New URL for search
]
