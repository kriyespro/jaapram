from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),
    path('overview/', views.user_dashboard, name='overview'),  # Alias for user_dashboard
    path('statistics/', views.user_statistics, name='user_statistics'),
    path('targets/', views.user_targets, name='user_targets'),
    path('targets/set/', views.set_targets, name='set_targets'),
    path('achievements/', views.user_achievements, name='user_achievements'),
] 