from django.core.management.base import BaseCommand

from football.services.sync import sync_current


class Command(BaseCommand):
    help = "Sync SLEEPER_USERNAME's current-season leagues (hourly)."

    def handle(self, *args, **opts):
        ids = sync_current()
        self.stdout.write(f"synced leagues: {', '.join(ids)}")
