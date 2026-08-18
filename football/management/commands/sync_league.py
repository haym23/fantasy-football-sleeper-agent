from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from football.services.sync import sync_league, sync_user_season


class Command(BaseCommand):
    help = "One-time sync of league metadata, users, drafts and picks."

    def add_arguments(self, parser):
        parser.add_argument("--league-id", help="Sync a single league by ID")
        parser.add_argument("--season", help="Sync all of SLEEPER_USERNAME's leagues for a season (e.g. 2023)")

    def handle(self, *args, **opts):
        if opts["league_id"]:
            self.stdout.write(str(sync_league(opts["league_id"])))
        elif opts["season"]:
            ids = sync_user_season(settings.SLEEPER_USERNAME, opts["season"])
            self.stdout.write(f"synced leagues: {', '.join(ids)}")
        else:
            raise CommandError("pass --league-id or --season")
