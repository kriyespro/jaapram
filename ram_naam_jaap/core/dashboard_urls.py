from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/', views.admin_users, name='users'),  # Alias for backward compatibility
    path('users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/', views.admin_user_detail, name='user_profile'),  # Alias for profile links
    path('statistics/', views.admin_statistics, name='admin_statistics'),
    path('jaap-counts/', views.admin_jaap_counts, name='admin_jaap_counts'),
    path('leaderboard/', views.admin_leaderboard, name='admin_leaderboard'),
    path('system-info/', views.admin_system_info, name='admin_system_info'),
    path('app-control/', views.admin_app_control, name='admin_app_control'),
    path('app-control/', views.admin_app_control, name='app_control'),  # Alias
    path('clear-cache/', views.admin_clear_cache, name='admin_clear_cache'),
    path('communities/', views.admin_communities, name='communities'),
    path('jaap-records/', views.admin_jaap_records, name='jaap_records'),
    path('events/', views.admin_events, name='events'),
    path('content/', views.admin_content, name='content'),
    path('reports/', views.admin_reports, name='reports'),
    path('activity/', views.admin_activity, name='activity'),
    
    # Add missing URL patterns to prevent NoReverseMatch errors
    path('', views.admin_dashboard, name='index'),  # Index alias
    # Community management URLs (placeholders until proper views are created)
    path('communities/add/', views.admin_dashboard, name='add_community'),
    path('communities/<int:community_id>/edit/', views.admin_dashboard, name='edit_community'),
    path('communities/<int:community_id>/view/', views.admin_dashboard, name='view_community'),
    path('communities/<int:community_id>/members/', views.admin_dashboard, name='community_members'),
    path('communities/<int:community_id>/archive/', views.admin_dashboard, name='archive_community'),
    path('communities/<int:community_id>/restore/', views.admin_dashboard, name='restore_community'),
    path('communities/<int:community_id>/delete/', views.admin_dashboard, name='delete_community'),
    # User management URLs
    path('users/add/', views.admin_dashboard, name='add_user'),
    path('users/<int:user_id>/edit/', views.admin_dashboard, name='edit_user'),
    path('users/<int:user_id>/toggle-status/', views.admin_dashboard, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', views.admin_dashboard, name='delete_user'),
] 