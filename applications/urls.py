from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.application_list, name='application_list'),
    # path('create/<int:program_id>/', views.create_application, name='create_application'),
    path('create-from-search/<int:program_id>/', views.create_application_from_search, name='create_application_from_search'),
    path('create-for-university/<int:uni_id>/', views.create_application_for_university, name='create_application_for_university'), # New URL for applying to uni directly
    # Switching definitively to integer PK to resolve persistent NoReverseMatch error
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('<int:pk>/cancel/', views.cancel_application, name='cancel_application'),
    path('<int:pk>/documents/', views.manage_documents, name='manage_documents'),
    path('<int:pk>/documents/upload/<str:document_type>/', views.upload_document, name='upload_document'),
    path('<int:pk>/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
    path('<int:pk>/notes/add/', views.add_note, name='add_note'),
]
