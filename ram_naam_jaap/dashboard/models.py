from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Target(models.Model):
    """Model to track user's jaap targets"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='target')
    daily_target = models.PositiveIntegerField(default=108)
    weekly_target = models.PositiveIntegerField(default=756)  # 108 * 7
    monthly_target = models.PositiveIntegerField(default=3240)  # 108 * 30
    yearly_target = models.PositiveIntegerField(default=39420)  # 108 * 365
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s targets"
    
    @property
    def daily_progress(self):
        """Return the progress towards daily target as a percentage"""
        from jaap.models import JaapCount
        today = timezone.now().date()
        today_count = JaapCount.objects.filter(user=self.user, date=today).first()
        count = today_count.count if today_count else 0
        return min(100, (count / self.daily_target) * 100) if self.daily_target > 0 else 0
    
    @property
    def weekly_progress(self):
        """Return the progress towards weekly target as a percentage"""
        from jaap.models import JaapCount
        from datetime import timedelta
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        week_counts = JaapCount.objects.filter(
            user=self.user, 
            date__gte=week_start, 
            date__lte=today
        )
        
        total_count = sum(count.count for count in week_counts)
        return min(100, (total_count / self.weekly_target) * 100) if self.weekly_target > 0 else 0
    
    @property
    def monthly_progress(self):
        """Return the progress towards monthly target as a percentage"""
        from jaap.models import JaapCount
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        month_counts = JaapCount.objects.filter(
            user=self.user, 
            date__gte=month_start, 
            date__lte=today
        )
        
        total_count = sum(count.count for count in month_counts)
        return min(100, (total_count / self.monthly_target) * 100) if self.monthly_target > 0 else 0
    
    @property
    def yearly_progress(self):
        """Return the progress towards yearly target as a percentage"""
        from jaap.models import JaapCount
        
        today = timezone.now().date()
        year_start = today.replace(month=1, day=1)
        
        year_counts = JaapCount.objects.filter(
            user=self.user, 
            date__gte=year_start, 
            date__lte=today
        )
        
        total_count = sum(count.count for count in year_counts)
        return min(100, (total_count / self.yearly_target) * 100) if self.yearly_target > 0 else 0


class Achievement(models.Model):
    """Model to track user achievements"""
    ACHIEVEMENT_TYPES = (
        ('count', 'Count Milestone'),
        ('streak', 'Streak Milestone'),
        ('daily', 'Daily Target'),
        ('weekly', 'Weekly Target'),
        ('monthly', 'Monthly Target'),
        ('yearly', 'Yearly Target'),
        ('special', 'Special Achievement'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    achieved_at = models.DateTimeField(default=timezone.now)
    icon = models.CharField(max_length=50, default='trophy')  # CSS class for icon
    
    class Meta:
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
