from django.shortcuts import render

from football.models import Leagues
from football.services import llm


def chat_page(request):
    return render(request, "football/chat.html")


def chat_send(request):
    """HTMX target: returns the user's message + the LLM answer as a partial."""
    message = request.POST.get("message", "").strip()
    answer = llm.chat(message) if message else ""
    return render(request, "football/_chat_exchange.html", {"message": message, "answer": answer})


def players_page(request):
    query = request.GET.get("query", "")
    position = request.GET.get("position", "")
    players = llm.lookup_players(query=query, position=position, limit=100) if (query or position) else []
    return render(
        request,
        "football/players.html",
        {"players": players, "query": query, "position": position, "positions": ["QB", "RB", "WR", "TE", "K", "DEF"]},
    )


def league_page(request, league_id):
    league = Leagues.objects.get(league_id=league_id)
    return render(
        request,
        "football/league.html",
        {
            "league": league,
            "leagues": Leagues.objects.all().order_by("-season"),
            "transactions": llm.get_recent_transactions(league_id, limit=30),
            "news": llm.search_news(days=14)[:15],
        },
    )
