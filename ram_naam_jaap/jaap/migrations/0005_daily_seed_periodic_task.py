from django.db import migrations


def create_periodic_task(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    # 3:17 AM daily — off-peak, and a non-round minute so it doesn't line up
    # with anyone else's on-the-hour cron/beat jobs on the same box.
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="17", hour="3", day_of_week="*", day_of_month="*", month_of_year="*",
        defaults={"timezone": "Asia/Kolkata"},
    )

    PeriodicTask.objects.get_or_create(
        name="Daily seed devotees",
        defaults={
            "task": "jaap.tasks.daily_seed_devotees",
            "crontab": schedule,
            "enabled": True,
        },
    )


def remove_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="Daily seed devotees").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("jaap", "0004_jaap_perf_indexes"),
        ("django_celery_beat", "0018_improve_crontab_helptext"),
    ]

    operations = [
        migrations.RunPython(create_periodic_task, remove_periodic_task),
    ]
