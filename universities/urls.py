from django.urls import path
from . import views

app_name = 'universities'

urlpatterns = [
    path('', views.university_list, name='university_list'),
    path('<slug:slug>/', views.university_detail, name='university_detail'),
    path('<slug:uni_slug>/programs/', views.program_list, name='program_list'),
    path('<slug:uni_slug>/programs/<slug:prog_slug>/', views.program_detail, name='program_detail'),
    path('search/', views.search_universities, name='search_universities'),
    path('filter/', views.filter_universities, name='filter_universities'),
    path('compare/', views.compare_universities, name='compare_universities'),
] 