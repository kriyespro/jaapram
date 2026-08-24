from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import UserProfile
from .forms import UserProfileForm, UserForm
from django.utils import timezone

from dashboard.models import Target
from jaap.models import JaapCount


@login_required
def profile_view(request):
    """View for user's profile"""
    user = request.user

    target, _ = Target.objects.get_or_create(user=user, defaults={'daily_target': 108})
    daily_target = target.daily_target or 108

    today = timezone.now().date()
    today_obj = JaapCount.objects.filter(user=user, date=today).first()
    today_count = today_obj.count if today_obj else 0
    today_pct = min(100, int((today_count / daily_target) * 100)) if daily_target else 0

    recent_entries = JaapCount.objects.filter(user=user).order_by('-date')[:5]

    context = {
        'user': user,
        'today_count': today_count,
        'daily_target': daily_target,
        'today_pct': today_pct,
        'total_jaap_count': user.profile.total_jaap_count,
        'streak_days': user.profile.streak_days,
        'recent_entries': recent_entries,
    }

    return render(request, 'accounts/profile.html', context)


@login_required
@transaction.atomic
def edit_profile(request):
    """View for editing user's profile"""
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/edit_profile.html', context)
