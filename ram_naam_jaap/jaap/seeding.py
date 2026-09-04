"""
Fake-devotee seed data: shared by the initial seed command and the daily
celery task, so both stay in sync with one implementation.

Seed users are marked by an @example.com email (same convention the older
generate_dummy_data command already used) — real signups never get that
domain, so `is_seed_user()` cheaply tells fake from real without a schema
change.
"""
import random
import secrets

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from accounts.models import UserProfile
from jaap.models import JaapCount
from jaap.management.commands.generate_dummy_data import (
    HINDU_FIRST_NAMES,
    HINDU_LAST_NAMES,
    INDIAN_CITIES,
)

DAILY_JAAP = 108
SEED_EMAIL_DOMAIN = "example.com"


def is_seed_user(user: User) -> bool:
    return user.email.endswith(f"@{SEED_EMAIL_DOMAIN}")


def seed_devotees_queryset():
    return User.objects.filter(email__endswith=f"@{SEED_EMAIL_DOMAIN}", is_active=True)


def _invalidate_stat_caches():
    """New devotees / new jaap should show up immediately, not after the
    leaderboard's 1-hour cache (or the home page's 60s one) expires."""
    cache.delete('global_leaderboard')
    cache.delete('home_page_stats')


def _unique_username(first_name, last_name):
    for _ in range(20):
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 9999)}"
        if not User.objects.filter(username=username).exists():
            return username
    return f"devotee{random.randint(100000, 999999)}"


def create_seed_devotees(count):
    """Create `count` new fake devotees, each with a profile city and
    today's 108 jaap already logged. Returns the list of created User rows."""
    today = timezone.now().date()
    created = []
    with transaction.atomic():
        for _ in range(count):
            first_name = random.choice(HINDU_FIRST_NAMES)
            last_name = random.choice(HINDU_LAST_NAMES)
            username = _unique_username(first_name, last_name)
            user = User.objects.create_user(
                username=username,
                email=f"{username}@{SEED_EMAIL_DOMAIN}",
                password=secrets.token_urlsafe(12),
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
            # post_save signal already created a blank UserProfile — set its city.
            UserProfile.objects.filter(user=user).update(city=random.choice(INDIAN_CITIES))
            created.append(user)

    # Bulk-insert today's jaap in one query (skip per-row .save(), so
    # cumulative_count stays 0 on these rows — only cosmetic, admin-only
    # display; the real totals everywhere else use Sum('count')).
    JaapCount.objects.bulk_create(
        [JaapCount(user=u, date=today, count=DAILY_JAAP) for u in created],
        ignore_conflicts=True,
    )
    if created:
        _invalidate_stat_caches()
    return created


def run_daily_seed(new_devotees=11, jaap_per_devotee=DAILY_JAAP):
    """The once-a-day cron job: add `new_devotees` fresh fake devotees, and
    log `jaap_per_devotee` for every existing fake devotee that doesn't
    already have an entry for today (safe to re-run — idempotent per day).
    One bulk_create for all of it: lowest possible DB load for the size."""
    today = timezone.now().date()

    new_users = create_seed_devotees(new_devotees)
    new_user_ids = {u.id for u in new_users}

    existing_ids = set(
        seed_devotees_queryset().exclude(id__in=new_user_ids).values_list("id", flat=True)
    )
    already_done_today = set(
        JaapCount.objects.filter(date=today, user_id__in=existing_ids).values_list(
            "user_id", flat=True
        )
    )
    due_ids = existing_ids - already_done_today

    JaapCount.objects.bulk_create(
        [JaapCount(user_id=uid, date=today, count=jaap_per_devotee) for uid in due_ids],
        ignore_conflicts=True,
    )
    if due_ids:
        _invalidate_stat_caches()

    return {
        "new_devotees": len(new_users),
        "existing_devotees_updated": len(due_ids),
    }
