import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from accounts.models import UserProfile
from jaap.models import JaapCount

# Lists of Hindu first names (male and female)
HINDU_MALE_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Krishna", "Ram", "Atharva", "Darsh", "Ishaan",
    "Shiva", "Yash", "Dhruv", "Kabir", "Ansh", "Neel", "Aryan", "Arnav", "Rudra", "Shivansh",
    "Veer", "Abhimanyu", "Harsh", "Pranav", "Krish", "Arush", "Sai", "Ved", "Lakshay", "Rohan",
    "Shaurya", "Parth", "Karan", "Naksh", "Virat", "Kartik", "Rishaan", "Agastya", "Samar", "Advaith",
    "Shresth", "Vedant", "Hrithik", "Laksh", "Manan", "Prem", "Pranay", "Soham", "Varun", "Tanish",
]

HINDU_FEMALE_NAMES = [
    "Saanvi", "Aanya", "Aadhya", "Aaradhya", "Ananya", "Pari", "Anika", "Navya", "Diya", "Divya",
    "Kashvi", "Vanya", "Kavya", "Nitya", "Anvi", "Myra", "Mahika", "Ira", "Kyra", "Avni",
    "Amaira", "Trisha", "Riya", "Kiara", "Pranavi", "Anjali", "Lakshmi", "Sita", "Radha", "Gauri",
    "Parvati", "Durga", "Meera", "Ganga", "Saraswati", "Shreya", "Aishwarya", "Aditi", "Nisha", "Priya",
    "Deepika", "Isha", "Tara", "Ahana", "Anisha", "Rashi", "Kaira", "Navya", "Kimaya", "Amrita",
]

# Combine male and female names
HINDU_FIRST_NAMES = HINDU_MALE_NAMES + HINDU_FEMALE_NAMES

# List of Hindu last names (surnames)
HINDU_LAST_NAMES = [
    "Sharma", "Verma", "Agarwal", "Patel", "Shah", "Mehta", "Gupta", "Singh", "Kumar", "Joshi",
    "Rao", "Reddy", "Nair", "Menon", "Pillai", "Iyer", "Iyengar", "Kulkarni", "Deshmukh", "Patil",
    "Shastri", "Trivedi", "Pandey", "Dwivedi", "Mishra", "Shukla", "Deshpande", "Jain", "Tiwari", "Chaturvedi",
    "Bhatt", "Dutta", "Kamath", "Hegde", "Acharya", "Rao", "Naidu", "Banerjee", "Chatterjee", "Sen",
    "Das", "Bose", "Sinha", "Yadav", "Chauhan", "Rathore", "Chopra", "Mehra", "Khanna", "Kapoor",
]

# List of major Indian cities
INDIAN_CITIES = [
    "Ayodhya", "Varanasi", "Mathura", "Haridwar", "Rishikesh", "Vrindavan", "Ujjain", "Puri", "Tirupati",
    "Dwarka", "Shirdi", "Amarnath", "Badrinath", "Kedarnath", "Gokarna", "Madurai", "Rameshwaram",
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", 
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna", "Vadodara", 
    "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Meerut", "Rajkot", "Amritsar", "Allahabad", "Ranchi",
    "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Raipur", "Kota", "Chandigarh",
    "Mysore", "Mangalore", "Thiruvananthapuram", "Bhubaneswar", "Salem", "Aligarh", "Gurugram", 
]

class Command(BaseCommand):
    help = 'Generate dummy devotees with Hindu names and add jaap counts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['create', 'update'],
            help='Action to perform: "create" new devotees or "update" existing ones'
        )
        
        parser.add_argument(
            '--count',
            type=int,
            default=108,
            help='Number of dummy devotees to create (default: 108, used with "create" action)'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'create':
            self.create_dummy_devotees(options['count'])
        elif action == 'update':
            self.update_all_devotee_jaap_counts()
    
    def generate_password(self):
        """Generate a random secure password."""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(12))
    
    def create_dummy_devotees(self, count=108):
        """Create dummy devotee accounts with Hindu names and cities."""
        created_count = 0
        
        try:
            with transaction.atomic():
                for i in range(count):
                    # Generate a unique username
                    first_name = random.choice(HINDU_FIRST_NAMES)
                    last_name = random.choice(HINDU_LAST_NAMES)
                    username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
                    
                    # Check if username already exists
                    if User.objects.filter(username=username).exists():
                        continue
                    
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        email=f"{username}@example.com",
                        password=self.generate_password(),
                        first_name=first_name,
                        last_name=last_name,
                        is_active=True
                    )
                    
                    # Create or update profile
                    city = random.choice(INDIAN_CITIES)
                    try:
                        profile = UserProfile.objects.get(user=user)
                        profile.city = city
                        profile.save()
                    except UserProfile.DoesNotExist:
                        # If the profile doesn't exist automatically via signals, create it
                        UserProfile.objects.create(
                            user=user,
                            city=city,
                            devotee_since=timezone.now() - timedelta(days=random.randint(1, 365))
                        )
                    
                    # Add initial jaap counts
                    self.add_jaap_counts_for_user(user)
                    
                    created_count += 1
                    self.stdout.write(f"Created devotee {created_count}: {first_name} {last_name} from {city}")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} dummy devotees!"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating dummy devotees: {e}"))
    
    def get_all_dummy_devotees(self):
        """Get all dummy devotees by checking for example.com email addresses."""
        return User.objects.filter(email__endswith='@example.com', is_active=True)
    
    def add_jaap_counts_for_user(self, user):
        """Add random jaap counts for a given user for the past week."""
        # Generate random jaap counts for the past 7 days
        today = timezone.now().date()
        
        # Hindu-specific sacred counts
        sacred_counts = [108, 216, 432, 648, 864, 1008]
        
        for i in range(7):
            date = today - timedelta(days=i)
            
            # Use either a sacred count or a random number between 108 and 1008
            if random.random() < 0.3:  # 30% chance of using a sacred count
                count = random.choice(sacred_counts)
            else:
                # Ensure count is at least 108 and at most 1008
                count = random.randint(108, 1008)
            
            # Check if entry already exists for this date
            existing_count = JaapCount.objects.filter(user=user, date=date).first()
            
            if existing_count:
                # Update existing count
                existing_count.count += count
                existing_count.save()
                self.stdout.write(f"Updated {user.username}'s count for {date} to {existing_count.count}")
            else:
                # Create new count
                JaapCount.objects.create(user=user, date=date, count=count)
                self.stdout.write(f"Added {count} jaaps for {user.username} on {date}")
    
    def update_all_devotee_jaap_counts(self):
        """Add random jaap counts for all dummy devotees for today."""
        dummy_devotees = self.get_all_dummy_devotees()
        today = timezone.now().date()
        
        update_count = 0
        
        # Hindu-specific sacred counts
        sacred_counts = [108, 216, 432, 648, 864, 1008]
        
        for user in dummy_devotees:
            # Check if we already have an entry for today
            existing_count = JaapCount.objects.filter(user=user, date=today).first()
            
            # Use either a sacred count or a random number between 108 and 1008
            if random.random() < 0.3:  # 30% chance of using a sacred count
                count = random.choice(sacred_counts)
            else:
                # Ensure count is at least 108 and at most 1008
                count = random.randint(108, 1008)
            
            if existing_count:
                # Update existing count
                existing_count.count += count
                existing_count.save()
            else:
                # Create new count
                JaapCount.objects.create(user=user, date=today, count=count)
            
            update_count += 1
            
            if update_count % 10 == 0:
                self.stdout.write(f"Updated {update_count} devotees...")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully updated jaap counts for {update_count} devotees for {today}!")) 