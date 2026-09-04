import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="jaap.tasks.daily_seed_devotees")
def daily_seed_devotees():
    """Runs once a day (see CrontabSchedule in migration 0005): adds 11 new
    fake devotees and logs 108 jaap for every existing fake devotee that
    hasn't got today's entry yet. One task, bulk DB writes, no per-user
    sub-tasks — keeps this off the critical path and cheap on server load."""
    from jaap.seeding import run_daily_seed

    result = run_daily_seed()
    logger.info("daily_seed_devotees: %s", result)
    return result
