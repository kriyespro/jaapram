from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import F, Sum
from django.core.cache import cache
from django.conf import settings
from django.contrib import messages
from datetime import datetime, timedelta
import requests
import json

from .models import JaapSession, JaapCount, JaapEntry, CityJaapCount
from dashboard.models import Target, Achievement
from accounts.models import UserProfile

import redis


def get_location_from_ip(ip_address):
    """Get city and country information from IP using ip-api.com"""
    if ip_address in ('127.0.0.1', 'localhost', '::1') or settings.DEBUG:
        # Return default location for development
        return {
            'status': 'success',
            'city': 'Ayodhya',
            'country': 'India',
            'lat': 26.7922,
            'lon': 82.1998
        }
    
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data['status'] == 'success':
            return {
                'status': 'success',
                'city': data.get('city', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0)
            }
        return {
            'status': 'error',
            'city': 'Unknown',
            'country': 'Unknown',
            'lat': 0,
            'lon': 0
        }
    except Exception as e:
        return {
            'status': 'error',
            'city': 'Unknown',
            'country': 'Unknown',
            'lat': 0,
            'lon': 0,
            'error': str(e)
        }


@login_required
def jaap_entry(request):
    """Main Jaap entry page with the form to type Ram"""
    # Get daily target
    target, created = Target.objects.get_or_create(user=request.user, defaults={'daily_target': 108})
    daily_target = target.daily_target
    
    # Get today's count
    today = timezone.now().date()
    today_count_obj, created = JaapCount.objects.get_or_create(
        user=request.user, 
        date=today,
        defaults={'count': 0}
    )
    today_count = today_count_obj.count
    
    # Calculate percentage
    percentage = min(int((today_count / daily_target) * 100), 100) if daily_target > 0 else 0
    
    # Get recent entries for the past 7 days
    recent_entries = []
    for i in range(7):
        day = today - timedelta(days=i)
        day_name = day.strftime('%A')
        try:
            entry = JaapCount.objects.get(user=request.user, date=day)
            recent_entries.append({
                'date': day,
                'count': entry.count,
                'day_name': day_name
            })
        except JaapCount.DoesNotExist:
            if i == 0:  # Only add today if it doesn't exist
                recent_entries.append({
                    'date': day,
                    'count': 0,
                    'day_name': day_name
                })
    
    # Format today's date in ISO format for the date input field
    today_date_iso = today.strftime('%Y-%m-%d')
    
    context = {
        'today_count': today_count,
        'daily_target': daily_target,
        'percentage': percentage,
        'recent_entries': recent_entries,
        'today_date_iso': today_date_iso,
    }
    
    return render(request, 'jaap/entry.html', context)


@login_required
@require_POST
def increment_jaap(request):
    """AJAX view to increment jaap count"""
    # Get current session
    session = JaapSession.objects.filter(
        user=request.user, 
        end_time=None
    ).first()
    
    if not session:
        # Create a new session if none exists
        session = JaapSession.objects.create(
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            device_info=request.META.get('HTTP_USER_AGENT', '')
        )
    
    # Get session key for cache
    session_key = f"jaap:session:{request.user.id}:{timezone.now().date()}"
    
    try:
        # Try to use Redis through Django's cache framework
        current_count = cache.get(session_key, 0)
        count = current_count + 1
        cache.set(session_key, count)
    except Exception as e:
        # Fallback to using the database if cache fails
        if session.count is None:
            session.count = 0
        session.count += 1
        session.save()
        count = session.count
    
    # Update session count in the database
    session.count = count
    session.save()
    
    # Every 10 counts, update the database for persistence
    if count % 10 == 0 or request.GET.get('force_update'):
        # Update today's count
        today = timezone.now().date()
        today_count, created = JaapCount.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'count': 0}
        )
        
        today_count.count = count
        today_count.save()
        
        # Update city count (only every 10 counts to minimize API calls)
        ip_address = request.META.get('REMOTE_ADDR')
        location = get_location_from_ip(ip_address)
        
        if location['status'] == 'success':
            CityJaapCount.update_count(
                city=location['city'],
                country=location['country'],
                latitude=location['lat'],
                longitude=location['lon'],
                count_to_add=10 if count > 10 else count  # Add 10 or the actual count if less
            )
        
        # Check for achievements when count is a multiple of 100
        if count % 100 == 0:
            check_achievements(request.user, count)
    
    # Prepare HTMX response
    if request.htmx:
        return HttpResponse(f"<span>{count}</span>")
    
    return JsonResponse({
        'count': count, 
        'session_id': session.id
    })


@login_required
def jaap_history(request):
    """View to show user's jaap history"""
    # Get all user's sessions
    sessions = JaapSession.objects.filter(user=request.user).order_by('-start_time')
    
    # Get daily counts
    daily_counts = JaapCount.objects.filter(user=request.user).order_by('-date')
    
    context = {
        'sessions': sessions,
        'daily_counts': daily_counts,
    }
    
    return render(request, 'jaap/history.html', context)


@login_required
def jaap_session_detail(request, session_id):
    """View to show details of a specific jaap session"""
    session = get_object_or_404(JaapSession, id=session_id, user=request.user)
    
    context = {
        'session': session,
    }
    
    return render(request, 'jaap/session_detail.html', context)


@login_required
@require_POST
def save_entry(request):
    """Save jaap entry from form submission"""
    count = request.POST.get('count', 0)
    
    try:
        count = int(count)
        if count < 0:
            raise ValueError("Count cannot be negative")
    except (ValueError, TypeError):
        messages.error(request, "Invalid count value")
        return redirect('jaap:jaap_entry')
    
    # If count is zero, just redirect back
    if count == 0:
        return redirect('jaap:jaap_entry')
    
    # Get date from form or use today
    date_str = request.POST.get('date')
    if date_str:
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            entry_date = timezone.now().date()
    else:
        entry_date = timezone.now().date()
    
    # Get or create JaapCount for the day
    jaap_count, created = JaapCount.objects.get_or_create(
        user=request.user,
        date=entry_date,
        defaults={'count': 0}
    )
    
    # Add the new count to the existing count
    jaap_count.count += count
    jaap_count.save()
    
    # Get or create an active session
    active_session = JaapSession.objects.filter(
        user=request.user, 
        end_time=None
    ).first()
    
    if not active_session:
        # Create a new session
        active_session = JaapSession.objects.create(
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            device_info=request.META.get('HTTP_USER_AGENT', '')
        )
    
    # Update session count
    active_session.count += count
    active_session.save()
    
    # Check for achievements
    if jaap_count.count >= 108 or count >= 108:
        check_achievements(request.user, jaap_count.count)
    
    messages.success(request, f"{count} Ram Naam Jaap{'s' if count > 1 else ''} recorded successfully!")
    return redirect('jaap:jaap_entry')


@login_required
@require_POST
def manual_entry(request):
    """Process manual entry form"""
    date_str = request.POST.get('date')
    count_str = request.POST.get('count')
    notes = request.POST.get('notes', '')
    
    if not date_str or not count_str:
        messages.error(request, "Date and count are required fields")
        return redirect('jaap:jaap_entry')
    
    try:
        count = int(count_str)
        if count <= 0:
            raise ValueError("Count must be positive")
    except (ValueError, TypeError):
        messages.error(request, "Count must be a positive number")
        return redirect('jaap:jaap_entry')
    
    try:
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Invalid date format")
        return redirect('jaap:jaap_entry')
    
    # Create a new entry
    entry = JaapEntry.objects.create(
        user=request.user,
        date=entry_date,
        count=count,
        notes=notes
    )
    
    # Update the daily total
    jaap_count, created = JaapCount.objects.get_or_create(
        user=request.user,
        date=entry_date,
        defaults={'count': 0}
    )
    
    jaap_count.count += count
    jaap_count.save()
    
    # Update profile total_jaaps
    profile = UserProfile.objects.get(user=request.user)
    profile.total_jaaps += count
    profile.save()
    
    # Update streak
    update_streak(request.user)
    
    # Update city count
    ip_address = request.META.get('REMOTE_ADDR')
    location = get_location_from_ip(ip_address)
    
    if location['status'] == 'success':
        CityJaapCount.update_count(
            city=location['city'],
            country=location['country'],
            latitude=location['lat'],
            longitude=location['lon'],
            count_to_add=count
        )
    
    # Check for achievements
    check_achievements(request.user, jaap_count.count)
    
    messages.success(request, f"Successfully added {count} jaaps on {entry_date.strftime('%Y-%m-%d')}")
    return redirect('jaap:jaap_entry')


def check_achievements(user, count):
    """Check and create achievements for the user based on count"""
    # Count-based achievements
    count_milestones = [
        (108, "First Mala Completed", "You've completed your first mala of 108 Ram Naam Jaap!"),
        (1008, "1008 Milestone", "You've reached 1008 Ram Naam Jaaps!"),
        (10800, "10,800 Milestone", "You've reached 10,800 Ram Naam Jaaps!"),
        (21600, "21,600 Milestone", "You've reached 21,600 Ram Naam Jaaps!"),
        (108000, "108,000 Milestone", "You've reached 108,000 Ram Naam Jaaps! Amazing dedication!"),
    ]
    
    for milestone, title, description in count_milestones:
        if count >= milestone:
            # Check if this achievement already exists
            achievement_exists = Achievement.objects.filter(
                user=user,
                achievement_type='count',
                title=title
            ).exists()
            
            if not achievement_exists:
                Achievement.objects.create(
                    user=user,
                    achievement_type='count',
                    title=title,
                    description=description
                )
    
    # Check streak achievements
    streak = user.profile.streak_days
    streak_milestones = [
        (7, "One Week Streak", "You've completed Ram Naam Jaap for 7 consecutive days!"),
        (21, "Three Week Streak", "You've completed Ram Naam Jaap for 21 consecutive days!"),
        (30, "One Month Streak", "You've completed Ram Naam Jaap for 30 consecutive days!"),
        (108, "108 Day Streak", "You've completed Ram Naam Jaap for 108 consecutive days! Amazing dedication!"),
    ]
    
    for milestone, title, description in streak_milestones:
        if streak >= milestone:
            # Check if this achievement already exists
            achievement_exists = Achievement.objects.filter(
                user=user,
                achievement_type='streak',
                title=title
            ).exists()
            
            if not achievement_exists:
                Achievement.objects.create(
                    user=user,
                    achievement_type='streak',
                    title=title,
                    description=description
                )
    
    # Check target achievements
    try:
        target = user.target
        
        # Get today's count
        today = timezone.now().date()
        today_count = JaapCount.objects.filter(user=user, date=today).first()
        
        if today_count and today_count.count >= target.daily_target:
            # Daily target achieved
            achievement_exists = Achievement.objects.filter(
                user=user,
                achievement_type='daily',
                title=f"Daily Target Achieved: {today.strftime('%Y-%m-%d')}",
            ).exists()
            
            if not achievement_exists:
                Achievement.objects.create(
                    user=user,
                    achievement_type='daily',
                    title=f"Daily Target Achieved: {today.strftime('%Y-%m-%d')}",
                    description=f"You've achieved your daily target of {target.daily_target} Ram Naam Jaaps!"
                )
    except Target.DoesNotExist:
        pass


@login_required
def input_jaap(request):
    """
    View for the Ram Naam input page - allows users to type Ram multiple times
    """
    # Get daily target and latest count if available
    target, created = Target.objects.get_or_create(
        user=request.user,
        defaults={'daily_target': 108}
    )
    
    today = datetime.now().date()
    today_entry = JaapEntry.objects.filter(
        user=request.user,
        date=today
    ).aggregate(total=Sum('count'))
    
    today_count = today_entry['total'] or 0
    
    # Get recent entries
    recent_entries = JaapEntry.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')[:5]
    
    # Format today's date for the date input
    today_date_iso = today.strftime('%Y-%m-%d')
    
    context = {
        'daily_target': target.daily_target,
        'today_count': today_count,
        'recent_entries': recent_entries,
        'today_date_iso': today_date_iso,
    }
    
    return render(request, 'jaap/input.html', context)


def get_today_total_jaap():
    """Get the total jaap count for today across all users"""
    today = timezone.now().date()
    cache_key = f"jaap:total:today:{today}"
    
    # Try to get from cache first
    cached_count = cache.get(cache_key)
    if cached_count is not None:
        return cached_count
    
    # Query the database if not cached
    total = JaapCount.objects.filter(date=today).aggregate(Sum('count'))['count__sum'] or 0
    
    # Cache for 5 minutes
    cache.set(cache_key, total, 300)
    
    return total


def map_data(request):
    """API view to provide city-based jaap count data for the map"""
    today = timezone.now().date()
    
    # Get today's city data
    city_data = CityJaapCount.objects.filter(date=today)
    
    # Format data for map
    map_data = []
    for city in city_data:
        map_data.append({
            'city': city.city,
            'country': city.country,
            'count': city.count,
            'lat': city.latitude,
            'lng': city.longitude
        })
    
    # Get today's total
    today_total = get_today_total_jaap()
    
    return JsonResponse({
        'city_data': map_data,
        'today_total': today_total,
        'timestamp': timezone.now().isoformat()
    })
