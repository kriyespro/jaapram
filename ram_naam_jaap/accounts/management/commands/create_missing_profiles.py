from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create user profiles for users that do not have one'

    def handle(self, *args, **options):
        users_without_profiles = []
        for user in User.objects.all():
            try:
                # Try to access the profile
                user.profile
            except User.profile.RelatedObjectDoesNotExist:
                # If profile doesn't exist, add to list
                users_without_profiles.append(user)
        
        # Create profiles for users that don't have one
        created_count = 0
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} missing user profiles'
            )
        ) 