from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='home'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('leaderboard/global/', views.global_leaderboard, name='global_leaderboard'),
    path('leaderboard/city/', views.city_leaderboard, name='city_leaderboard'),
    path('leaderboard/city/<str:city>/', views.city_detail_leaderboard, name='city_detail_leaderboard'),
    path('statistics/', views.community_statistics, name='statistics'),
] 