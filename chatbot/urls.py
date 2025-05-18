from django.urls import path
from . import views

app_name = 'chatbot' # Define the app namespace

urlpatterns = [
    path('api/chat/', views.chat_with_ai, name='chat_api'),
    # Add other chatbot-related URLs here if needed, e.g., for rendering an interface
    # path('', views.chat_interface, name='chat_interface'),
]
