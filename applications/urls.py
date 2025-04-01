from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.application_list, name='application_list'),
    # path('create/<int:program_id>/', views.create_application, name='create_application'),
    path('create-from-search/<int:program_id>/', views.create_application_from_search, name='create_application_from_search'),
    path('create-for-university/<int:uni_id>/', views.create_application_for_university, name='create_application_for_university'), # New URL for applying to uni directly
    path('<uuid:application_id>/', views.application_detail, name='application_detail'),
    path('<uuid:application_id>/edit/', views.edit_application, name='edit_application'),
    path('<uuid:application_id>/cancel/', views.cancel_application, name='cancel_application'),
    path('<uuid:application_id>/documents/', views.manage_documents, name='manage_documents'),
    path('<uuid:application_id>/documents/upload/<str:document_type>/', views.upload_document, name='upload_document'),
    path('<uuid:application_id>/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('<uuid:application_id>/status/', views.update_status, name='update_status'),
    path('<uuid:application_id>/notes/add/', views.add_note, name='add_note'),
]
