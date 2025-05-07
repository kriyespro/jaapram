from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    city = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def total_jaap_count(self):
        """Return the total Jaap count for the user"""
        from jaap.models import JaapCount
        return JaapCount.objects.filter(user=self.user).aggregate(
            total=models.Sum('count')
        )['total'] or 0
    
    @property
    def streak_days(self):
        """Return the current streak (consecutive days of Jaap) for the user"""
        from jaap.models import JaapCount
        from datetime import datetime, timedelta
        
        # Get all user's jaap counts ordered by date descending
        jaap_counts = JaapCount.objects.filter(user=self.user).order_by('-date')
        
        if not jaap_counts:
            return 0
        
        # Start with the latest date
        streak = 1
        latest_date = jaap_counts.first().date
        current_date = latest_date
        
        # If the latest date is not today, then streak might be broken
        today = datetime.now().date()
        if (today - latest_date).days > 1:
            return 0
        
        # Check consecutive days
        for count in jaap_counts[1:]:
            expected_date = current_date - timedelta(days=1)
            if count.date == expected_date:
                streak += 1
                current_date = count.date
            else:
                break
        
        return streak


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved"""
    instance.profile.save()
