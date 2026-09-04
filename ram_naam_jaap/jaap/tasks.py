import logging
import random

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="jaap.tasks.daily_seed_devotees")
def daily_seed_devotees():
    """Runs once a day (see CrontabSchedule in migration 0005): adds a
    handful of new fake devotees and logs 108 jaap for every existing fake
    devotee that hasn't got today's entry yet. One task, bulk DB writes, no
    per-user sub-tasks — keeps this off the critical path and cheap on
    server load."""
    from jaap.seeding import run_daily_seed

    # Randomized around 11/day (7-15) instead of a fixed count, so the
    # "new users" trend doesn't read as an obviously robotic flat line.
    new_devotees = random.randint(7, 15)

    result = run_daily_seed(new_devotees=new_devotees)
    logger.info("daily_seed_devotees: %s", result)
    return result
