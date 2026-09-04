from django.db import migrations


def switch_to_hourly(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    # Every hour at :23 — spreads fake joins/jaap across the day instead of
    # one fixed-time daily batch (see jaap.seeding.run_hourly_seed).
    hourly_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="23", hour="*", day_of_week="*", day_of_month="*", month_of_year="*",
        defaults={"timezone": "Asia/Kolkata"},
    )

    PeriodicTask.objects.filter(name="Daily seed devotees").update(
        name="Hourly seed devotees", crontab=hourly_schedule
    )


def switch_back_to_daily(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    daily_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="17", hour="3", day_of_week="*", day_of_month="*", month_of_year="*",
        defaults={"timezone": "Asia/Kolkata"},
    )
    PeriodicTask.objects.filter(name="Hourly seed devotees").update(
        name="Daily seed devotees", crontab=daily_schedule
    )


class Migration(migrations.Migration):

    dependencies = [
        ("jaap", "0005_daily_seed_periodic_task"),
    ]

    operations = [
        migrations.RunPython(switch_to_hourly, switch_back_to_daily),
    ]
