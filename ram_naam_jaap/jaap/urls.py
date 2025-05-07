from django.urls import path
from . import views

app_name = 'jaap'

urlpatterns = [
    path('', views.jaap_entry, name='jaap_entry'),
    path('increment/', views.increment_jaap, name='increment_jaap'),
    path('manual_entry/', views.manual_entry, name='manual_entry'),
    path('save_entry/', views.save_entry, name='save_entry'),
    path('history/', views.jaap_history, name='jaap_history'),
    path('session/<int:session_id>/', views.jaap_session_detail, name='jaap_session_detail'),
    path('input/', views.input_jaap, name='input_jaap'),
    path('api/map-data/', views.map_data, name='map_data'),
] 