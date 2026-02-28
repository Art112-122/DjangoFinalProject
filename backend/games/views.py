import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import ServiceForm, ReviewForm
from .models import Service, Game, Review
from authentication.models import User

user_action_logger = logging.getLogger("user_actions")


def index(request):
    games = Game.objects.all()
    latest_services = Service.objects.select_related("game", "author").order_by("-id")[
        :6
    ]

    return render(
        request,
        "games/index.html",
        {"games": games, "latest_services": latest_services},
    )


def game_catalog_view(request):

    game_id = request.GET.get("game")

    if game_id:
        game_obj = get_object_or_404(Game, id=game_id)

        services = Service.objects.filter(game=game_obj)
    else:
        game_obj = Game.objects.first()
        services = Service.objects.filter(game=game_obj)

    return render(
        request,
        "catalog.html",
        {
            "game": game_obj,
            "services": services,
        },
    )


# Servises


def service_catalog(request):
    game_id = request.GET.get("game")
    search_query = request.GET.get("search")
    page_number = request.GET.get("page", 1)

    services = Service.objects.all().order_by("-id")

    if game_id:
        game_obj = get_object_or_404(Game, id=game_id)
        services = services.filter(game=game_obj)
    else:
        game_obj = None

    if search_query:
        services = services.filter(title__icontains=search_query)

    paginator = Paginator(services, 12)
    page_obj = paginator.get_page(page_number)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "games/_service_items.html", {"services": page_obj})

    return render(
        request,
        "games/catalog.html",
        {
            "game": game_obj,
            "services": page_obj,
            "search_query": search_query,
        },
    )


def service_detail(request, pk):
    service = get_object_or_404(Service.objects.select_related("author", "game"), pk=pk)
    avg_rating = service.reviews.aggregate(Avg("rating"))["rating__avg"] or 0

    full_stars = int(avg_rating)

    user_already_reviewed = False
    if request.user.is_authenticated:
        user_already_reviewed = Review.objects.filter(
            service=service, author=request.user
        ).exists()

    return render(
        request,
        "games/service_detail.html",
        {
            "service": service,
            "avg_rating": round(avg_rating, 1),
            "full_stars": range(full_stars),
            "empty_stars": range(5 - full_stars),
            "user_already_reviewed": user_already_reviewed,
        },
    )


@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, author=request.user)

    if request.method == "POST":
        service.delete()
        user_action_logger.info(f"✅DELETE: Обьявление удалено: {service.title}")
        messages.success(request, "Объявление удалено.")

    return redirect("profile")


@login_required
def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.author = request.user
            service.save()
            user_action_logger.info(
                f"✅CREATE: Обьявление {service.title} создано автором {request.user}"
            )
            return redirect("profile")

    else:
        form = ServiceForm()
    return render(
        request, "games/service_form.html", {"form": form, "title": "Создать услугу"}
    )


@login_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk, author=request.user)
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            user_action_logger.info(
                f"♻️UPDATE: Обьявление {service.title} обновлено автором {request.user}"
            )
            return redirect("profile")
    else:
        form = ServiceForm(instance=service)
    return render(
        request,
        "games/service_form.html",
        {"form": form, "title": "Редактировать услугу"},
    )


def add_review(request, service_id):
    service = Service.objects.get(id=service_id)
    if request.method == "POST" and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.author = request.user
            review.save()
            user_action_logger.info(
                f"✅CREATE: Пользыватель {request.user} оставил отзыв под обьявлением {service.title}"
            )
    return redirect("service_detail", pk=service_id)


def add_to_cart(request, service_id):
    if request.method == "POST":
        get_object_or_404(Service, id=service_id)

        cart = request.session.get("cart", [])

        if service_id not in cart:
            cart.append(service_id)
            request.session["cart"] = cart

        return JsonResponse(
            {
                "status": "success",
                "cart_count": len(cart),
                "total_items": len(cart),
            }
        )
    return JsonResponse({"status": "error"}, status=400)


def cart_detail(request):
    cart_ids = request.session.get("cart", [])
    services = Service.objects.filter(id__in=cart_ids)
    total_price = sum(service.price for service in services)
    return render(
        request, "games/cart.html", {"services": services, "total_price": total_price}
    )


def remove_from_cart(request, service_id):
    if request.method == "POST":
        cart = request.session.get("cart", [])
        if service_id in cart:
            cart.remove(service_id)
            request.session["cart"] = cart

        services = Service.objects.filter(id__in=cart)
        total_price = sum(service.price for service in services)

        return JsonResponse(
            {
                "status": "success",
                "cart_count": len(cart),
                "total_price": float(total_price),
            }
        )


def get_cart_count(request):
    cart = request.session.get("cart", [])
    return JsonResponse({"total_items": len(cart)})


def seller_profile(request, email):
    seller = get_object_or_404(User, email=email)
    services = Service.objects.filter(author=seller)

    return render(
        request,
        "games/seller_profile.html",
        {
            "seller": seller,
            "services": services,
        },
    )
