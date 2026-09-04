from django.core.management.base import BaseCommand

from jaap.seeding import create_seed_devotees


class Command(BaseCommand):
    help = (
        "One-off: create an initial batch of fake Indian devotees (108 jaap "
        "logged for today each). Run once to seed the platform; after that "
        "the 'Daily seed devotees' celery beat task adds 11/day on its own."
    )

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=108, help="Devotees to create (default 108)")

    def handle(self, *args, **options):
        created = create_seed_devotees(options["count"])
        self.stdout.write(self.style.SUCCESS(f"Created {len(created)} seed devotees, 108 jaap each for today."))
