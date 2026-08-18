from django.core.management.base import BaseCommand

from football.services.sync import sync_players


class Command(BaseCommand):
    help = "Refresh the NFL player catalog from Sleeper (weekly)."

    def handle(self, *args, **opts):
        self.stdout.write(f"players synced: {sync_players()}")
