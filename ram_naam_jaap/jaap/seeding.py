"""
Fake-devotee seed data: shared by the initial seed command and the hourly
celery task, so both stay in sync with one implementation.

Seed users are marked by an @example.com email (same convention the older
generate_dummy_data command already used) — real signups never get that
domain, so `is_seed_user()` cheaply tells fake from real without a schema
change.
"""
import random
import secrets
from zoneinfo import ZoneInfo

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

SEED_EMAIL_DOMAIN = "example.com"
IST = ZoneInfo("Asia/Kolkata")

# Traditional japa counts — not a flat 108 for everyone. Weighted so 108 is
# still the single most common value, but real variety shows up on the
# leaderboard instead of a suspiciously identical number for every devotee.
SACRED_COUNTS = [11, 21, 51, 108, 216, 501, 1008]
SACRED_COUNT_WEIGHTS = [10, 10, 15, 35, 15, 10, 5]

# Per-hour chance an as-yet-unlogged devotee gets today's jaap this run.
# With an hourly cron, 1-(1-0.25)^24 ≈ 99.9% chance any given devotee is
# covered well before the day ends; the last-hour force-flush below is the
# backstop for that remaining ~0.1%.
HOURLY_COVERAGE_PROBABILITY = 0.25


def is_seed_user(user: User) -> bool:
    return user.email.endswith(f"@{SEED_EMAIL_DOMAIN}")


def seed_devotees_queryset():
    return User.objects.filter(email__endswith=f"@{SEED_EMAIL_DOMAIN}", is_active=True)


def random_jaap_count():
    return random.choices(SACRED_COUNTS, weights=SACRED_COUNT_WEIGHTS)[0]


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
    """Create `count` new fake devotees, each with a profile city and a
    random japa count already logged for today. Returns the created Users."""
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
        [JaapCount(user=u, date=today, count=random_jaap_count()) for u in created],
        ignore_conflicts=True,
    )
    if created:
        _invalidate_stat_caches()
    return created


def run_hourly_seed(new_devotee_range=(0, 2)):
    """The once-an-hour cron job (see migration 0006): joins trickle in
    across the day instead of arriving in one fixed daily batch, and each
    devotee's jaap for the day is logged at a random hour with a random
    traditional count (11/21/51/108/...), not a uniform 108 for everyone at
    a fixed time. Safe to re-run any hour — only tops up devotees who don't
    already have today's entry. One bulk query per run either way."""
    now_ist = timezone.localtime(timezone.now(), IST)
    today = now_ist.date()
    is_last_hour_of_day = now_ist.hour == 23

    new_users = create_seed_devotees(random.randint(*new_devotee_range))
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

    if is_last_hour_of_day:
        # Backstop: everyone still missing today's jaap gets it now, so
        # "all seed devotees jaap daily" holds even on an unlucky day.
        chosen_ids = due_ids
    else:
        chosen_ids = {uid for uid in due_ids if random.random() < HOURLY_COVERAGE_PROBABILITY}

    JaapCount.objects.bulk_create(
        [JaapCount(user_id=uid, date=today, count=random_jaap_count()) for uid in chosen_ids],
        ignore_conflicts=True,
    )
    if chosen_ids or new_users:
        _invalidate_stat_caches()

    return {
        "new_devotees": len(new_users),
        "existing_devotees_updated": len(chosen_ids),
        "still_due_today": len(due_ids) - len(chosen_ids),
    }
