from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.contrib import messages
from django.conf import settings

from datetime import timedelta
import os
import sys
import django
import json

# Try to import optional dependencies
try:
    import psutil
except ImportError:
    psutil = None

try:
    import redis
except ImportError:
    redis = None

from jaap.models import JaapCount, JaapSession
from accounts.models import UserProfile

User = get_user_model()

# Helper function to check if user is staff
def is_staff(user):
    return user.is_staff

# Path helpers
def page_view(request, template, context=None):
    """Render a page with standard context"""
    context = context or {}
    return render(request, template, context)


def home_view(request):
    """Home page view"""
    # If user is logged in, redirect to jaap entry
    if request.user.is_authenticated:
        return redirect('jaap:jaap_entry')
    
    # Get total jaap count and user count for display
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    user_count = User.objects.filter(is_active=True).count()
    
    # Get top users for home page leaderboard
    top_users = User.objects.annotate(
        total_jaap=Sum('jaap_counts__count')
    ).filter(
        total_jaap__gt=0
    ).order_by('-total_jaap')[:10]
    
    # Get top 5 cities
    top_cities = UserProfile.objects.exclude(
        city=''
    ).values('city').annotate(
        user_count=Count('user')
    ).order_by('-user_count')[:5]
    
    # Create chart data for activity over time
    seven_days_ago = timezone.now().date() - timezone.timedelta(days=7)
    daily_counts = JaapCount.objects.filter(
        date__gte=seven_days_ago
    ).values('date').annotate(
        day_total=Sum('count')
    ).order_by('date')
    
    # Prepare chart data
    chart_labels = [count['date'].strftime('%b %d') for count in daily_counts]
    chart_data = [count['day_total'] for count in daily_counts]
    
    context = {
        'total_count': total_count,
        'total_users': user_count,
        'top_users': top_users,
        'top_cities': top_cities,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'pages/home.html', context)


def about_view(request):
    """About page view"""
    return page_view(request, 'pages/about.html')


def privacy_view(request):
    """Privacy policy page view"""
    return page_view(request, 'pages/privacy.html')


def terms_view(request):
    """Terms of service page view"""
    return page_view(request, 'pages/terms.html')


@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    """Admin dashboard view with system overview"""
    # Get stats for the dashboard
    total_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    total_users = User.objects.filter(is_active=True).count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    
    # Get active jaap sessions
    active_sessions = JaapSession.objects.filter(end_time=None).count()
    
    # Get recent activity
    recent_users = User.objects.filter(is_active=True).order_by('-last_login')[:5]
    recent_jaap_counts = JaapCount.objects.order_by('-date')[:5]
    
    # Get daily counts for mini chart
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    daily_counts = JaapCount.objects.filter(
        date__gte=seven_days_ago
    ).values('date').annotate(
        day_total=Sum('count')
    ).order_by('date')
    
    # Context for template
    context = {
        'total_count': total_count,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'active_sessions': active_sessions,
        'recent_users': recent_users,
        'recent_jaap_counts': recent_jaap_counts,
        'daily_counts': daily_counts,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def admin_users(request):
    """Admin users view with filtering and searching"""
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    filter_by = request.GET.get('filter', 'all')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply filters
    if filter_by == 'active':
        users = users.filter(is_active=True)
    elif filter_by == 'inactive':
        users = users.filter(is_active=False)
    elif filter_by == 'staff':
        users = users.filter(is_staff=True)
    elif filter_by == 'superuser':
        users = users.filter(is_superuser=True)
    
    # Apply search
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Order by most recently joined
    users = users.order_by('-date_joined')
    
    # Get user counts by status for the sidebar
    user_counts = {
        'all': User.objects.count(),
        'active': User.objects.filter(is_active=True).count(),
        'inactive': User.objects.filter(is_active=False).count(),
        'staff': User.objects.filter(is_staff=True).count(),
        'superuser': User.objects.filter(is_superuser=True).count(),
    }
    
    # Context for template
    context = {
        'users': users,
        'user_counts': user_counts,
        'search_query': search_query,
        'filter_by': filter_by,
    }
    
    return render(request, 'admin/users.html', context)


@login_required
@user_passes_test(is_staff)
def admin_user_detail(request, user_id):
    """Admin view for detailed user information"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's jaap counts
    jaap_counts = JaapCount.objects.filter(user=user).order_by('-date')
    
    # Calculate user stats
    total_jaap = jaap_counts.aggregate(total=Sum('count'))['total'] or 0
    jaap_days = jaap_counts.values('date').distinct().count()
    
    # Calculate average daily count
    if jaap_days > 0:
        avg_daily = total_jaap / jaap_days
    else:
        avg_daily = 0
    
    # Get user's recent sessions
    recent_sessions = JaapSession.objects.filter(user=user).order_by('-start_time')[:10]
    
    # Context for template
    context = {
        'user_profile': user,
        'jaap_counts': jaap_counts[:30],  # Limit to 30 days
        'total_jaap': total_jaap,
        'jaap_days': jaap_days,
        'avg_daily': avg_daily,
        'recent_sessions': recent_sessions,
    }
    
    return render(request, 'admin/user_detail.html', context)


@login_required
@user_passes_test(is_staff)
def admin_statistics(request):
    """Admin statistics view with comprehensive data analysis"""
    # Time period filter
    period = request.GET.get('period', '30d')
    
    if period == '7d':
        days_ago = 7
    elif period == '90d':
        days_ago = 90
    elif period == '365d':
        days_ago = 365
    else:  # Default to 30 days
        days_ago = 30
    
    start_date = timezone.now().date() - timedelta(days=days_ago)
    
    # Get daily counts
    daily_counts = JaapCount.objects.filter(
        date__gte=start_date
    ).values('date').annotate(
        day_total=Sum('count')
    ).order_by('date')
    
    # Get user registration over time
    user_signups = User.objects.filter(
        date_joined__date__gte=start_date
    ).extra({'date': "date(date_joined)"}).values(
        'date'
    ).annotate(
        count=Count('id')
    ).order_by('date')
    
    # Get top users for the period
    top_users = User.objects.filter(
        jaap_counts__date__gte=start_date
    ).annotate(
        period_total=Sum('jaap_counts__count')
    ).filter(
        period_total__gt=0
    ).order_by('-period_total')[:10]
    
    # Get city statistics
    city_stats = UserProfile.objects.filter(
        user__jaap_counts__date__gte=start_date
    ).values('city').annotate(
        total=Sum('user__jaap_counts__count'),
        user_count=Count('user', distinct=True)
    ).filter(
        city__isnull=False,
        city__ne=''
    ).order_by('-total')[:10]
    
    # Context for template
    context = {
        'daily_counts': daily_counts,
        'user_signups': user_signups,
        'top_users': top_users,
        'city_stats': city_stats,
        'period': period,
        'days_ago': days_ago,
    }
    
    return render(request, 'admin/statistics.html', context)


@login_required
@user_passes_test(is_staff)
def admin_jaap_counts(request):
    """Admin jaap counts view with filtering options"""
    # Filter options
    date_filter = request.GET.get('date', '')
    user_filter = request.GET.get('user', '')
    
    # Base queryset
    jaap_counts = JaapCount.objects.all()
    
    # Apply filters
    if date_filter:
        jaap_counts = jaap_counts.filter(date=date_filter)
    
    if user_filter:
        # Could be username or user ID
        try:
            if user_filter.isdigit():
                jaap_counts = jaap_counts.filter(user_id=int(user_filter))
            else:
                jaap_counts = jaap_counts.filter(user__username__icontains=user_filter)
        except ValueError:
            pass
    
    # Order by most recent
    jaap_counts = jaap_counts.order_by('-date')[:100]  # Limit to 100 for performance
    
    # Context for template
    context = {
        'jaap_counts': jaap_counts,
        'date_filter': date_filter,
        'user_filter': user_filter,
    }
    
    return render(request, 'admin/jaap_counts.html', context)


@login_required
@user_passes_test(is_staff)
def admin_leaderboard(request):
    """Admin leaderboard view with additional options"""
    # Get filter options
    period = request.GET.get('period', 'all')
    city = request.GET.get('city', '')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply period filter to jaap count calculation
    if period == 'today':
        today = timezone.now().date()
        users = users.annotate(
            total_jaap=Sum('jaap_counts__count', filter=Q(jaap_counts__date=today))
        )
    elif period == 'week':
        week_ago = timezone.now().date() - timedelta(days=7)
        users = users.annotate(
            total_jaap=Sum('jaap_counts__count', filter=Q(jaap_counts__date__gte=week_ago))
        )
    elif period == 'month':
        month_ago = timezone.now().date() - timedelta(days=30)
        users = users.annotate(
            total_jaap=Sum('jaap_counts__count', filter=Q(jaap_counts__date__gte=month_ago))
        )
    else:  # Default to all time
        users = users.annotate(
            total_jaap=Sum('jaap_counts__count')
        )
    
    # Apply city filter if provided
    if city:
        users = users.filter(profile__city__icontains=city)
    
    # Filter out users with no jaaps and order by count
    users = users.filter(total_jaap__gt=0).order_by('-total_jaap')[:50]
    
    # Get list of cities for filter dropdown
    cities = UserProfile.objects.exclude(city='').values_list('city', flat=True).distinct()
    
    # Context for template
    context = {
        'top_users_by_count': users,
        'period': period,
        'city': city,
        'cities': cities,
    }
    
    return render(request, 'admin/leaderboard.html', context)


@login_required
@user_passes_test(is_staff)
def admin_system_info(request):
    """Admin view for system information and diagnostics"""
    # Get Django version
    django_version = django.__version__
    
    # Get Python version and path
    python_version = sys.version
    python_path = sys.executable
    
    # Get system information
    system_info = {
        'platform': sys.platform,
        'cpu_count': os.cpu_count(),
    }
    
    # Add psutil-dependent metrics if available
    if psutil:
        try:
            system_info.update({
                'memory_total': psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
                'memory_available': psutil.virtual_memory().available / (1024 * 1024 * 1024),  # GB
                'disk_total': psutil.disk_usage('/').total / (1024 * 1024 * 1024),  # GB
                'disk_free': psutil.disk_usage('/').free / (1024 * 1024 * 1024),  # GB
            })
        except Exception as e:
            system_info.update({
                'memory_total': 'N/A (psutil error)',
                'memory_available': 'N/A (psutil error)',
                'disk_total': 'N/A (psutil error)',
                'disk_free': 'N/A (psutil error)',
                'error': str(e)
            })
    else:
        system_info.update({
            'memory_total': 'N/A (psutil not installed)',
            'memory_available': 'N/A (psutil not installed)',
            'disk_total': 'N/A (psutil not installed)',
            'disk_free': 'N/A (psutil not installed)',
        })
    
    # Check Redis connection
    redis_status = 'Not Installed'
    if redis:
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            r = redis.from_url(redis_url, socket_connect_timeout=1)
            r.ping()
            redis_status = 'Online'
        except Exception:
            redis_status = 'Offline'
    
    # Check database connection
    try:
        db_status = 'Online' if User.objects.first() is not None else 'Empty'
    except Exception:
        db_status = 'Error'
    
    # Get installed apps
    installed_apps = settings.INSTALLED_APPS
    
    # Context for template
    context = {
        'django_version': django_version,
        'python_version': python_version,
        'python_path': python_path,
        'system_info': system_info,
        'redis_status': redis_status,
        'db_status': db_status,
        'installed_apps': installed_apps,
        'debug_mode': settings.DEBUG,
    }
    
    return render(request, 'admin/system_info.html', context)


@login_required
@user_passes_test(is_staff)
def admin_app_control(request):
    """Admin view for application control settings"""
    # Handle form submission
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'clear_cache':
            # Clear cache
            cache.clear()
            messages.success(request, 'Cache cleared successfully!')
        
        elif action == 'clear_sessions':
            # Clear sessions (requires django.contrib.sessions)
            from django.contrib.sessions.models import Session
            Session.objects.all().delete()
            messages.success(request, 'All sessions cleared successfully!')
        
        return redirect('admin_dashboard:admin_app_control')
    
    # Get general system stats
    active_users_24h = User.objects.filter(last_login__gte=timezone.now() - timedelta(hours=24)).count()
    total_jaap_count = JaapCount.objects.aggregate(total=Sum('count'))['total'] or 0
    
    # Context for template
    context = {
        'active_users_24h': active_users_24h,
        'total_jaap_count': total_jaap_count,
    }
    
    return render(request, 'admin/app_control.html', context)


@login_required
@user_passes_test(is_staff)
def admin_clear_cache(request):
    """Admin view to clear cache and return to previous page"""
    # Clear the cache
    cache.clear()
    
    # Add success message
    messages.success(request, 'Cache cleared successfully!')
    
    # Redirect back to the referring page or dashboard
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:admin_dashboard'))


@login_required
@user_passes_test(is_staff)
def admin_communities(request):
    """Admin view for community management"""
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')
    
    # This view requires the community model - we'll provide a placeholder template
    # until the model is implemented
    
    # Mock data for template display
    mock_communities = [
        {
            'id': 1,
            'name': 'Ram Bhakts Delhi',
            'type': 'Local',
            'status': 'Active',
            'member_count': 124,
            'created_at': timezone.now() - timedelta(days=45),
            'last_activity': timezone.now() - timedelta(hours=3),
        },
        {
            'id': 2,
            'name': 'Global Jaap Community',
            'type': 'Global',
            'status': 'Active',
            'member_count': 352,
            'created_at': timezone.now() - timedelta(days=180),
            'last_activity': timezone.now() - timedelta(minutes=30),
        },
        {
            'id': 3,
            'name': 'Temple Group Mumbai',
            'type': 'Temple',
            'status': 'Archived',
            'member_count': 78,
            'created_at': timezone.now() - timedelta(days=120),
            'last_activity': timezone.now() - timedelta(days=15),
        },
    ]
    
    context = {
        'communities': mock_communities,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    
    return render(request, 'admin/communities.html', context)


@login_required
@user_passes_test(is_staff)
def admin_jaap_records(request):
    """Admin view for detailed jaap records"""
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    user_filter = request.GET.get('user', '')
    
    # Mock data for template display
    mock_records = [
        {
            'id': 1,
            'user': 'bhakt123',
            'date': timezone.now().date(),
            'count': 108,
            'duration': '01:30:00',
            'type': 'Mala',
            'notes': 'Morning session',
        },
        {
            'id': 2,
            'user': 'ramsharan',
            'date': timezone.now().date() - timedelta(days=1),
            'count': 1008,
            'duration': '03:15:00',
            'type': 'Mahajaap',
            'notes': 'Temple session',
        },
    ]
    
    context = {
        'jaap_records': mock_records,
        'date_from': date_from,
        'date_to': date_to,
        'user_filter': user_filter,
    }
    
    return render(request, 'admin/jaap_records.html', context)


@login_required
@user_passes_test(is_staff)
def admin_events(request):
    """Admin view for event management"""
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    # Mock data for template display
    mock_events = [
        {
            'id': 1,
            'title': 'Ram Navami Celebration',
            'date': timezone.now().date() + timedelta(days=10),
            'location': 'Delhi Temple',
            'status': 'Upcoming',
            'participants': 45,
            'organizer': 'Temple Committee',
        },
        {
            'id': 2,
            'title': 'Online Jaap Marathon',
            'date': timezone.now().date() + timedelta(days=5),
            'location': 'Virtual',
            'status': 'Upcoming',
            'participants': 120,
            'organizer': 'Global Jaap Community',
        },
        {
            'id': 3,
            'title': 'Monthly Satsang',
            'date': timezone.now().date() - timedelta(days=15),
            'location': 'Mumbai Hall',
            'status': 'Completed',
            'participants': 85,
            'organizer': 'Mumbai Bhakt Association',
        },
    ]
    
    context = {
        'events': mock_events,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/events.html', context)


@login_required
@user_passes_test(is_staff)
def admin_content(request):
    """Admin view for content management"""
    # Get filter parameters
    content_type = request.GET.get('type', 'all')
    
    # Mock data for template display
    mock_content = [
        {
            'id': 1,
            'title': 'Ram Charitra Manas Summary',
            'type': 'Article',
            'status': 'Published',
            'author': 'Admin',
            'created_at': timezone.now() - timedelta(days=30),
            'views': 1245,
        },
        {
            'id': 2,
            'title': 'Benefits of Ram Naam Jaap',
            'type': 'Article',
            'status': 'Published',
            'author': 'Admin',
            'created_at': timezone.now() - timedelta(days=15),
            'views': 753,
        },
        {
            'id': 3,
            'title': 'Ram Bhajans Collection',
            'type': 'Media',
            'status': 'Published',
            'author': 'Content Team',
            'created_at': timezone.now() - timedelta(days=7),
            'views': 421,
        },
    ]
    
    context = {
        'content_items': mock_content,
        'content_type': content_type,
    }
    
    return render(request, 'admin/content.html', context)


@login_required
@user_passes_test(is_staff)
def admin_reports(request):
    """Admin view for reports"""
    # Get filter parameters
    report_type = request.GET.get('type', 'user_growth')
    
    # Mock data for report
    if report_type == 'user_growth':
        report_data = {
            'title': 'User Growth Report',
            'subtitle': 'Last 30 days',
            'total_new_users': 127,
            'growth_percentage': 23.5,
            'chart_labels': [str(timezone.now().date() - timedelta(days=x)) for x in range(30, 0, -1)],
            'chart_data': [5, 7, 4, 3, 8, 6, 9, 3, 5, 4, 2, 3, 7, 8, 5, 3, 4, 6, 7, 3, 4, 5, 6, 8, 9, 5, 3, 2, 4, 6],
        }
    elif report_type == 'jaap_activity':
        report_data = {
            'title': 'Jaap Activity Report',
            'subtitle': 'Last 30 days',
            'total_jaaps': 25783,
            'avg_daily': 859.4,
            'chart_labels': [str(timezone.now().date() - timedelta(days=x)) for x in range(30, 0, -1)],
            'chart_data': [820, 932, 901, 934, 1290, 1330, 1320, 720, 855, 945, 765, 845, 925, 978, 785, 839, 918, 756, 843, 886, 921, 808, 865, 932, 975, 856, 798, 875, 932, 1012],
        }
    else:
        report_data = {
            'title': 'General Activity Report',
            'subtitle': 'System overview',
            'message': 'Please select a report type',
        }
    
    context = {
        'report_data': report_data,
        'report_type': report_type,
    }
    
    return render(request, 'admin/reports.html', context)


@login_required
@user_passes_test(is_staff)
def admin_activity(request):
    """Admin view for system activity log"""
    # Get filter parameters
    date_filter = request.GET.get('date', '')
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', 'all')
    
    # Mock data for activity log
    mock_activities = [
        {
            'id': 1,
            'user': 'admin',
            'action': 'User Login',
            'details': 'Admin login from 192.168.1.1',
            'timestamp': timezone.now() - timedelta(minutes=15),
            'ip_address': '192.168.1.1',
        },
        {
            'id': 2,
            'user': 'bhakt123',
            'action': 'Jaap Recorded',
            'details': 'Recorded 108 jaaps',
            'timestamp': timezone.now() - timedelta(hours=1),
            'ip_address': '192.168.1.45',
        },
        {
            'id': 3,
            'user': 'ramsharan',
            'action': 'Profile Updated',
            'details': 'Updated profile picture',
            'timestamp': timezone.now() - timedelta(hours=2),
            'ip_address': '192.168.1.72',
        },
        {
            'id': 4,
            'user': 'admin',
            'action': 'System Update',
            'details': 'Cache cleared',
            'timestamp': timezone.now() - timedelta(hours=4),
            'ip_address': '192.168.1.1',
        },
    ]
    
    context = {
        'activities': mock_activities,
        'date_filter': date_filter,
        'user_filter': user_filter,
        'action_filter': action_filter,
    }
    
    return render(request, 'admin/activity.html', context)
