from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from .models import Target, Achievement
from .forms import TargetForm
from jaap.models import JaapCount


@login_required
def user_dashboard(request):
    """Main dashboard view for the user"""
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
    
    # Get today's count
    today = timezone.now().date()
    today_count = JaapCount.objects.filter(
        user=request.user, 
        date=today
    ).first()
    
    # Get user's total count
    total_count = JaapCount.objects.filter(
        user=request.user
    ).aggregate(
        total=Sum('count')
    )['total'] or 0
    
    # Get recent achievements
    recent_achievements = Achievement.objects.filter(
        user=request.user
    ).order_by('-achieved_at')[:5]
    
    context = {
        'target': target,
        'today_count': today_count,
        'total_count': total_count,
        'recent_achievements': recent_achievements,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


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
