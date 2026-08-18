from django.core.management.base import BaseCommand, CommandError

from football.models import Leagues
from football.services.sync import sync_transactions


class Command(BaseCommand):
    help = "Sync the transaction log (hourly for active leagues)."

    def add_arguments(self, parser):
        parser.add_argument("--league-id", help="Sync one league (default: all in-season leagues)")

    def handle(self, *args, **opts):
        if opts["league_id"]:
            league_ids = [opts["league_id"]]
        else:
            league_ids = list(Leagues.objects.filter(status="in_season").values_list("league_id", flat=True))
            if not league_ids:
                raise CommandError("no in-season leagues; pass --league-id")
        for lid in league_ids:
            self.stdout.write(f"{lid}: {sync_transactions(lid)} transactions")
