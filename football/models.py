from django.db import models


class Players(models.Model):
    player_id = models.TextField(primary_key=True)
    full_name = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)
    team = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    injury_status = models.TextField(blank=True, null=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "players"
        indexes = [models.Index(fields=["position", "team"], name="idx_players_pos_team")]


class Leagues(models.Model):
    league_id = models.TextField(primary_key=True)
    name = models.TextField()
    season = models.TextField()
    status = models.TextField()
    total_rosters = models.IntegerField()
    draft_id = models.TextField(blank=True, null=True)
    roster_positions = models.TextField(blank=True, null=True)  # JSON array
    scoring_settings = models.TextField(blank=True, null=True)  # JSON object
    settings = models.TextField(blank=True, null=True)  # JSON object
    previous_league_id = models.TextField(blank=True, null=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leagues"


class Users(models.Model):
    pk = models.CompositePrimaryKey("user_id", "league_id")
    user_id = models.TextField()
    league_id = models.TextField()
    display_name = models.TextField()
    avatar = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "users"


class Drafts(models.Model):
    draft_id = models.TextField(primary_key=True)
    league_id = models.TextField()
    season = models.TextField()
    type = models.TextField()
    status = models.TextField()
    rounds = models.IntegerField()
    slots = models.IntegerField()
    draft_order = models.TextField(blank=True, null=True)  # JSON object
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drafts"


class DraftPicks(models.Model):
    pk = models.CompositePrimaryKey("draft_id", "round", "pick")
    draft_id = models.TextField()
    round = models.IntegerField()
    pick = models.IntegerField()
    roster_id = models.IntegerField()
    player_id = models.TextField(blank=True, null=True)
    picked_by = models.TextField(blank=True, null=True)
    is_keeper = models.IntegerField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)  # JSON object

    class Meta:
        db_table = "draft_picks"
        indexes = [
            models.Index(fields=["player_id"], name="idx_draft_picks_player"),
            models.Index(fields=["picked_by"], name="idx_draft_picks_user"),
        ]


class Transactions(models.Model):
    transaction_id = models.TextField(primary_key=True)
    league_id = models.TextField()
    type = models.TextField()
    status = models.TextField()
    created_at = models.IntegerField()  # epoch ms from Sleeper
    leg = models.IntegerField(blank=True, null=True)
    creator = models.TextField(blank=True, null=True)
    waiver_bid = models.IntegerField(blank=True, null=True)
    adds = models.TextField(blank=True, null=True)  # JSON object
    drops = models.TextField(blank=True, null=True)  # JSON object
    draft_picks = models.TextField(blank=True, null=True)  # JSON array
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        indexes = [models.Index(fields=["league_id", "type"], name="idx_transactions_league_type")]


class NewsItem(models.Model):
    player = models.ForeignKey(
        Players, on_delete=models.CASCADE, db_column="player_id", blank=True, null=True
    )
    source = models.TextField()  # e.g. "sleeper", "fantasy_life"
    headline = models.TextField()
    body = models.TextField(blank=True, null=True)
    url = models.TextField(unique=True)  # dedupe key for idempotent ingestion
    published_at = models.DateTimeField(blank=True, null=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "news"
        indexes = [models.Index(fields=["player", "published_at"], name="idx_news_player_date")]
