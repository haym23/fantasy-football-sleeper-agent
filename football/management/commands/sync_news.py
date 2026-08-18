from django.core.management.base import BaseCommand

from football.services.sync import sync_news


class Command(BaseCommand):
    help = "Ingest RSS news feeds into the news table (hourly)."

    def handle(self, *args, **opts):
        self.stdout.write(f"new items: {sync_news()}")
