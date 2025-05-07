from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.core.cache import cache
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
import json

from accounts.models import UserProfile
from jaap.models import JaapCount


def community_home(request):
    """Community home page with statistics and leaderboard"""
    # Get total Ram Naam count
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    
    # Get total users count
    total_users = User.objects.filter(is_active=True).count()
    
    # Get top 10 users for the leaderboard
    top_users = User.objects.annotate(
        total_jaap=Sum('jaap_counts__count')
    ).filter(
        total_jaap__gt=0
    ).order_by('-total_jaap')[:10]
    
    # Get recent activity
    recent_activity = JaapCount.objects.filter(
        count__gt=0
    ).select_related('user').order_by('-date')[:10]
    
    # Get top 5 cities
    top_cities = UserProfile.objects.exclude(
        city=''
    ).values('city').annotate(
        user_count=Count('user')
    ).order_by('-user_count')[:5]
    
    # Create a safe version of top_cities with URL-safe city names
    safe_top_cities = []
    for city_data in top_cities:
        safe_top_cities.append({
            'city': city_data['city'],
            'city_url': city_data['city'],  # This is used directly in URL
            'user_count': city_data['user_count']
        })
    
    # Get daily counts for the past 7 days for the activity chart
    seven_days_ago = timezone.now().date() - timezone.timedelta(days=7)
    daily_counts = JaapCount.objects.filter(
        date__gte=seven_days_ago
    ).values('date').annotate(
        day_total=Sum('count')
    ).order_by('date')
    
    # Prepare chart data
    chart_labels = [count['date'].strftime('%b %d') for count in daily_counts]
    chart_data = [count['day_total'] for count in daily_counts]
    
    # JSON encode the chart data
    chart_labels_json = json.dumps(chart_labels)
    chart_data_json = json.dumps(chart_data)
    
    context = {
        'total_count': total_count,
        'total_users': total_users,
        'top_users': top_users,
        'recent_activity': recent_activity,
        'top_cities': safe_top_cities,
        'chart_labels': chart_labels_json,
        'chart_data': chart_data_json,
    }
    
    return render(request, 'community/home.html', context)


def global_leaderboard(request):
    """Global leaderboard view"""
    # Cache key for the leaderboard
    cache_key = 'global_leaderboard'
    
    # Try to get the leaderboard from cache
    leaderboard = cache.get(cache_key)
    
    if not leaderboard:
        # If not in cache, fetch from database
        leaderboard = User.objects.annotate(
            total_jaap=Sum('jaap_counts__count')
        ).filter(
            total_jaap__gt=0
        ).select_related('profile').order_by('-total_jaap')[:100]
        
        # Cache the leaderboard for 1 hour
        cache.set(cache_key, leaderboard, 60 * 60)
    
    # Get global stats for the top of the page
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    active_users = User.objects.filter(jaap_counts__date__gte=timezone.now().date() - timezone.timedelta(days=30)).distinct().count()
    today_count = JaapCount.objects.filter(date=timezone.now().date()).aggregate(total=Sum('count'))['total'] or 0
    
    context = {
        'leaderboard': leaderboard,
        'total_count': total_count,
        'active_users': active_users,
        'today_count': today_count,
    }
    
    return render(request, 'community/global_leaderboard.html', context)


def city_leaderboard(request):
    """City-wise leaderboard view"""
    # Get all cities that have users
    cities = UserProfile.objects.exclude(
        city=''
    ).values_list(
        'city', flat=True
    ).distinct()
    
    # Get top user for each city
    city_leaders = {}
    for city in cities:
        leader = User.objects.filter(
            profile__city=city
        ).annotate(
            total_jaap=Sum('jaap_counts__count')
        ).filter(
            total_jaap__gt=0
        ).order_by('-total_jaap').first()
        
        if leader:
            city_leaders[city] = {
                'user': leader,
                'count': leader.total_jaap,
            }
    
    # Get global stats for the top of the page
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    active_users = User.objects.filter(jaap_counts__date__gte=timezone.now().date() - timezone.timedelta(days=30)).distinct().count()
    today_count = JaapCount.objects.filter(date=timezone.now().date()).aggregate(total=Sum('count'))['total'] or 0
    
    context = {
        'cities': cities,
        'city_leaders': city_leaders,
        'total_count': total_count, 
        'active_users': active_users,
        'today_count': today_count,
    }
    
    # Handle HTMX requests directly here instead of redirecting
    if request.headers.get('HX-Request'):
        selected_city = request.GET.get('city', '').strip()
        if selected_city:
            users = User.objects.filter(
                profile__city=selected_city
            ).annotate(
                total_jaap=Sum('jaap_counts__count')
            ).filter(
                total_jaap__gt=0
            ).order_by('-total_jaap')[:50]
            
            city_context = {
                'city': selected_city,
                'users': users
            }
            return render(request, 'community/city_detail_leaderboard_partial.html', city_context)
        
        return render(request, 'community/city_leaderboard_partial.html', context)
    
    return render(request, 'community/city_leaderboard.html', context)


def city_detail_leaderboard(request, city):
    """Detailed leaderboard for a specific city"""
    # Get users from the city
    users = User.objects.filter(
        profile__city=city
    ).annotate(
        total_jaap=Sum('jaap_counts__count')
    ).filter(
        total_jaap__gt=0
    ).order_by('-total_jaap')[:50]
    
    # Get global stats for the top of the page
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    active_users = User.objects.filter(jaap_counts__date__gte=timezone.now().date() - timezone.timedelta(days=30)).distinct().count()
    today_count = JaapCount.objects.filter(date=timezone.now().date()).aggregate(total=Sum('count'))['total'] or 0
    
    context = {
        'city': city,
        'users': users,
        'total_count': total_count,
        'active_users': active_users,
        'today_count': today_count,
    }
    
    # If this is an HTMX request, return just the partial template
    if request.headers.get('HX-Request'):
        return render(request, 'community/city_detail_leaderboard_partial.html', context)
    
    return render(request, 'community/city_detail_leaderboard.html', context)


def leaderboard(request):
    """Combined leaderboard view with all types (global, city, streak)"""
    # Get global stats
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    active_users = User.objects.filter(jaap_counts__date__gte=timezone.now().date() - timezone.timedelta(days=30)).distinct().count()
    today_count = JaapCount.objects.filter(date=timezone.now().date()).aggregate(total=Sum('count'))['total'] or 0
    
    # Get top users for global leaderboard
    top_users = User.objects.annotate(
        total=Sum('jaap_counts__count')
    ).filter(
        total__gt=0
    ).select_related('profile').order_by('-total')[:50]
    
    # Get all cities
    cities = UserProfile.objects.exclude(
        city=''
    ).values_list(
        'city', flat=True
    ).distinct()
    
    # Get top users by city
    top_users_by_city = []
    for city in cities:
        users = User.objects.filter(
            profile__city=city
        ).annotate(
            total=Sum('jaap_counts__count')
        ).filter(
            total__gt=0
        ).select_related('profile').order_by('-total')[:5]
        
        top_users_by_city.extend(users)
    
    # Sort city users by total count
    top_users_by_city = sorted(top_users_by_city, key=lambda x: x.total, reverse=True)[:50]
    
    # Get all users first, then filter and sort by streak property
    users_with_profiles = User.objects.select_related('profile').all()
    # Filter users with streak > 0 and sort by streak_days property
    users_with_streaks = [user for user in users_with_profiles if hasattr(user, 'profile') and user.profile.streak_days > 0]
    # Sort by streak_days property
    top_streaks = sorted(users_with_streaks, key=lambda user: user.profile.streak_days, reverse=True)[:50]
    
    context = {
        'total_count': total_count,
        'active_users': active_users,
        'today_count': today_count,
        'top_users': top_users,
        'top_users_by_city': top_users_by_city,
        'top_streaks': top_streaks,
        'cities': cities,
    }
    
    return render(request, 'community/leaderboard.html', context)


def community_statistics(request):
    """Community statistics view with charts and data"""
    # Get total Ram Naam count
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    
    # Get total users count
    total_users = User.objects.filter(is_active=True).count()
    
    # Get daily counts for the past 30 days
    thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
    daily_counts = JaapCount.objects.filter(
        date__gte=thirty_days_ago
    ).values('date').annotate(
        day_total=Sum('count')
    ).order_by('date')
    
    # Prepare chart data
    chart_labels = [count['date'].strftime('%Y-%m-%d') for count in daily_counts]
    chart_data = [count['day_total'] for count in daily_counts]
    
    # Get top 5 cities
    top_cities = UserProfile.objects.exclude(
        city=''
    ).values('city').annotate(
        user_count=Count('user')
    ).order_by('-user_count')[:5]
    
    context = {
        'total_count': total_count,
        'total_users': total_users,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'top_cities': top_cities,
    }
    
    return render(request, 'community/statistics.html', context)
