from .models import Game


def all_games_processor(request):
    return {"nav_games": Game.objects.all()}
