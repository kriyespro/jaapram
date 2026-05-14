from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import get_user_model
from datetime import timedelta

from .models import Target, Achievement
from .forms import TargetForm
from jaap.models import JaapCount

User = get_user_model()


@login_required
def user_dashboard(request):
    """Combined personal progress + community snapshot (single hub page)."""
    today = timezone.now().date()
    target, _ = Target.objects.get_or_create(
        user=request.user,
        defaults={
            'daily_target': 108,
            'weekly_target': 756,
            'monthly_target': 3240,
            'yearly_target': 39420,
        },
    )

    today_obj = JaapCount.objects.filter(user=request.user, date=today).first()
    my_today = today_obj.count if today_obj else 0
    daily_target = target.daily_target or 108
    my_daily_pct = min(100, int((my_today / daily_target) * 100)) if daily_target else 0

    week_start = today - timedelta(days=6)
    week_total = (
        JaapCount.objects.filter(
            user=request.user, date__gte=week_start, date__lte=today
        ).aggregate(t=Sum('count'))['t']
        or 0
    )
    weekly_target = target.weekly_target or 756
    my_week_pct = min(100, int((week_total / weekly_target) * 100)) if weekly_target else 0

    my_total = (
        JaapCount.objects.filter(user=request.user).aggregate(t=Sum('count'))['t'] or 0
    )

    profile = getattr(request.user, 'profile', None)
    my_streak = profile.streak_days if profile else 0

    global_total = JaapCount.objects.aggregate(t=Sum('count'))['t'] or 0
    global_members = User.objects.filter(is_active=True).count()
    top_users = (
        User.objects.annotate(total_jaap=Sum('jaap_counts__count'))
        .filter(total_jaap__gt=0)
        .select_related('profile')
        .order_by('-total_jaap')[:8]
    )
    recent_feed = (
        JaapCount.objects.filter(count__gt=0)
        .select_related('user')
        .order_by('-date', '-id')[:6]
    )

    context = {
        'target': target,
        'my_today': my_today,
        'my_daily_pct': my_daily_pct,
        'my_week_total': week_total,
        'my_week_pct': my_week_pct,
        'my_total': my_total,
        'my_streak': my_streak,
        'global_total': global_total,
        'global_members': global_members,
        'top_users': top_users,
        'recent_feed': recent_feed,
    }
    return render(request, 'dashboard/hub.html', context)


@login_required
def user_statistics(request):
    """Statistics view for the user"""
    # Get all user's counts
    counts = JaapCount.objects.filter(
        user=request.user
    ).order_by('-date')
    
    # Get last 30 days data for chart
    thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
    thirty_day_counts = JaapCount.objects.filter(
        user=request.user,
        date__gte=thirty_days_ago
    ).order_by('date')
    
    # Calculate streaks
    current_streak = request.user.profile.streak_days
    
    # Prepare chart data
    chart_labels = [count.date.strftime('%Y-%m-%d') for count in thirty_day_counts]
    chart_data = [count.count for count in thirty_day_counts]
    
    context = {
        'counts': counts,
        'current_streak': current_streak,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    
    return render(request, 'dashboard/statistics.html', context)


@login_required
def user_targets(request):
    """Targets view for the user"""
    # Get user's target
    target, created = Target.objects.get_or_create(
        user=request.user,
        defaults={
            'daily_target': 108,
            'weekly_target': 756,
            'monthly_target': 3240,
            'yearly_target': 39420
        }
    )
    
    context = {
        'target': target,
    }
    
    return render(request, 'dashboard/targets.html', context)


@login_required
def set_targets(request):
    """View to set user's targets"""
    # Get user's target
    target, created = Target.objects.get_or_create(
        user=request.user,
        defaults={
            'daily_target': 108,
            'weekly_target': 756,
            'monthly_target': 3240,
            'yearly_target': 39420
        }
    )
    
    if request.method == 'POST':
        form = TargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your targets have been updated!')
            return redirect('dashboard:user_targets')
    else:
        form = TargetForm(instance=target)
    
    context = {
        'form': form,
        'target': target,
    }
    
    return render(request, 'dashboard/set_targets.html', context)


@login_required
def user_achievements(request):
    """Achievements view for the user"""
    # Get all user's achievements
    achievements = Achievement.objects.filter(
        user=request.user
    ).order_by('-achieved_at')
    
    context = {
        'achievements': achievements,
    }
    
    return render(request, 'dashboard/achievements.html', context)
