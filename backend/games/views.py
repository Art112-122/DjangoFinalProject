from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Game


def game_catalog(request):
    games = Game.objects.all()
    return render(request, "games/catalog.html", {"games": games})



@require_POST
def add_to_cart(request, game_id):
    cart = request.session.get("cart", {})
    game_id = str(game_id)

    if game_id in cart:
        cart[game_id] += 1
    else:
        cart[game_id] = 1

    request.session["cart"] = cart

    total_items = sum(cart.values())

    return JsonResponse({"message": "added", "total_items": total_items})


def remove_from_cart(request, game_id):
    cart = request.session.get("cart", {})
    game_id = str(game_id)

    if game_id in cart:
        del cart[game_id]

    request.session["cart"] = cart
    return redirect("cart")


def cart_view(request):
    cart = request.session.get("cart", {})
    games = []
    total = 0

    for game_id, quantity in cart.items():
        game = get_object_or_404(Game, id=game_id)
        game.total_price = game.price * quantity
        game.quantity = quantity
        total += game.total_price
        games.append(game)

    return render(request, "games/cart.html", {"games": games, "total": total})

def cart_count(request):
    cart = request.session.get("cart", {})
    total_items = sum(cart.values())
    return JsonResponse({"total_items": total_items})
