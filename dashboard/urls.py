from django.urls import path
from . import views
from universities import views as universities_views # Import universities views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:user_id>/', views.student_detail, name='student_detail'),
    # consultant_list removed as requested
    path('consultants/<int:user_id>/', views.consultant_detail, name='consultant_detail'),
    path('applications/', views.application_overview, name='application_overview'),
    # analytics removed as requested
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('activities/', views.activity_log, name='activity_log'),
    path('search-universities/', views.university_search, name='university_search'), # University search (potentially for all users)

    # Consultant Specific URLs
    path('consultant/applications/', views.consultant_application_list, name='consultant_application_list'),
    # --- Use the view from universities app ---
    path('consultant/universities/', universities_views.consultant_university_list, name='consultant_university_list'),
    path('consultant/universities/add/', universities_views.consultant_add_university, name='consultant_add_university'), # Assuming this is also in universities.views
    path('consultant/universities/<int:uni_id>/edit/', universities_views.consultant_edit_university, name='consultant_edit_university'), # Assuming this is also in universities.views
    # Add URLs for university detail, program management if needed within consultant dashboard
    path('recommend/', views.recommend_universities, name='recommend_universities'),
]
