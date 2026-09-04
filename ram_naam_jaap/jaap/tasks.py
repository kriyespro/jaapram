import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="jaap.tasks.daily_seed_devotees")
def daily_seed_devotees():
    """Runs once an hour (see CrontabSchedule in migration 0006 — task name
    kept as-is so the existing PeriodicTask row doesn't need recreating).
    Joins trickle in through the day and each devotee's jaap for today lands
    at a random hour with a random traditional count, instead of one fixed
    daily batch at a fixed time with a uniform 108 for everyone. One bulk
    task, bulk DB writes, no per-user sub-tasks — cheap on server load even
    running 24x/day."""
    from jaap.seeding import run_hourly_seed

    result = run_hourly_seed()
    logger.info("daily_seed_devotees (hourly): %s", result)
    return result
