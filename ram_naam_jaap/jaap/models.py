from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JaapSession(models.Model):
    """Model to track individual jaap sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jaap_sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username}'s session on {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration(self):
        """Return the duration of the session in minutes"""
        if not self.end_time:
            return None
        
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 60  # Return minutes
    
    @property
    def is_active(self):
        """Return whether the session is still active"""
        return self.end_time is None
    
    def end_session(self):
        """End the current session"""
        self.end_time = timezone.now()
        self.save()


class JaapCount(models.Model):
    """Model to track daily jaap counts for each user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jaap_counts')
    date = models.DateField(default=timezone.now)
    count = models.PositiveIntegerField(default=0)
    cumulative_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username}'s count on {self.date}"
    
    def save(self, *args, **kwargs):
        # Calculate cumulative count
        if not self.cumulative_count:
            # Get previous day's cumulative count
            previous_counts = JaapCount.objects.filter(
                user=self.user, 
                date__lt=self.date
            ).order_by('-date')
            
            previous_cumulative = previous_counts.first().cumulative_count if previous_counts.exists() else 0
            self.cumulative_count = previous_cumulative + self.count
        
        super().save(*args, **kwargs)


class JaapEntry(models.Model):
    """Model to track individual jaap entries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jaap_entries')
    date = models.DateField(default=timezone.now)
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Jaap Entry'
        verbose_name_plural = 'Jaap Entries'
    
    def __str__(self):
        return f"{self.user.username}'s entry on {self.date}: {self.count} jaaps"


class CityJaapCount(models.Model):
    """Model to track jaap counts aggregated by city"""
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    count = models.PositiveIntegerField(default=0)
    date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date', 'city']
        verbose_name = 'City Jaap Count'
        verbose_name_plural = 'City Jaap Counts'
        unique_together = ['city', 'date']
    
    def __str__(self):
        return f"{self.city}, {self.country} - {self.count} jaaps on {self.date}"
    
    @classmethod
    def update_count(cls, city, country, latitude, longitude, count_to_add):
        """Update the jaap count for a city, creating a new record if needed"""
        today = timezone.now().date()
        city_count, created = cls.objects.get_or_create(
            city=city,
            country=country,
            date=today,
            defaults={
                'latitude': latitude,
                'longitude': longitude,
                'count': count_to_add,
                'timestamp': timezone.now()
            }
        )
        
        if not created:
            city_count.count += count_to_add
            city_count.timestamp = timezone.now()
            city_count.save()
        
        return city_count
