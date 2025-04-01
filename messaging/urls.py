from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('api/messages/<int:conversation_id>/mark-read/', views.mark_messages_read, name='mark_messages_read'),
] 