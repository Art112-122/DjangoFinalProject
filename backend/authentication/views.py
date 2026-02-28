"""
Auth views:
- Register (with form)
- Verify email
- Login (rate limit)
- Logout
"""

import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.cache import cache
from .models import User
from games.models import Cart, CartItem, Game, Service
from .services.verification_service import create_verification, verify_code
from .services.email_service import send_verification_email
from .forms import CustomUserCreationForm

user_action_logger = logging.getLogger("user_actions")

LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_BLOCK_TIME = 300


def merge_cart_from_cookies(request, user):
    cart_cookie = request.COOKIES.get("cart")
    if not cart_cookie:
        return

    try:
        cookie_data = json.loads(cart_cookie)
    except (json.JSONDecodeError, TypeError):
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for game_id, quantity in cookie_data.items():
        try:
            game = Game.objects.get(id=game_id)
            item, created = CartItem.objects.get_or_create(cart=user_cart, game=game)

            if not created:
                item.quantity += int(quantity)
            else:
                item.quantity = int(quantity)
            item.save()
        except (Game.DoesNotExist, ValueError):
            continue


def is_blocked(ip, email):
    key = f"login_attempts:{ip}:{email}"
    attempts = cache.get(key, 0)
    return attempts >= LOGIN_ATTEMPTS_LIMIT


def register_failed_attempt(ip, email):
    key = f"login_attempts:{ip}:{email}"
    attempts = cache.get(key, 0)
    cache.set(key, attempts + 1, timeout=LOGIN_BLOCK_TIME)


def home(request):
    return render(request, "games/catalog.html")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.is_active = False
            user.is_verified = False
            user.save()

            code = create_verification(user)
            send_verification_email(user, code)

            request.session["verification_user_id"] = user.id

            user_action_logger.info(
                f"✅ РЕГИСТРАЦИЯ: Пользователь {user.email} (ник: {user.username}) зарегистрировался"
            )

            messages.success(
                request,
                "Регистрация прошла успешно! Мы отправили код подтверждения на ваш Email.",
            )
            return redirect("verify_email")
        else:
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)

            user_action_logger.warning(
                f"❗ РЕГИСТРАЦИЯ: Пользователь {request.POST.get('email', 'Неизвестный')} получил предупреждение по этим пунктам {error_list}"
            )
    else:
        form = CustomUserCreationForm()

    return render(request, "authentication/register.html", {"form": form})


def verify_email_view(request):
    user_id = request.session.get("verification_user_id")
    if not user_id:
        return redirect("register")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("register")

    if request.method == "POST":
        code = request.POST.get("code")

        if verify_code(user, code):
            user.is_active = True
            user.is_verified = True
            user.save()
            login(request, user)

            user_action_logger.info(
                f"✅ ПОДТВЕРЖДЕНИЕ: Пользователь {user.email} подтвердил email"
            )

            messages.success(request, "Email подтверждён! Добро пожаловать.")
            return redirect("catalog")
        else:
            user_action_logger.warning(
                f"Неудачная попытка подтверждения email для {user.email}"
            )

            messages.error(request, "Неверный или просроченный код.")

    return render(request, "authentication/verify_email.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        ip = request.META.get("REMOTE_ADDR")

        if is_blocked(ip, email):
            messages.error(request, "Слишком много попыток. Попробуйте позже.")
            return redirect("login")

        user = authenticate(request, email=email, password=password)

        if user:
            if user.is_verified:
                cache.delete(f"login_attempts:{ip}:{email}")
                login(request, user)
                request.session.set_expiry(60 * 60 * 24 * 7)

                response = redirect("catalog")

                merge_cart_from_cookies(request, user)
                response.delete_cookie("cart")

                user_action_logger.info(f"✅ ВХОД: {email}")

                messages.success(request, "Вы успешно вошли.")
                return response
            else:
                messages.error(request, "Email не подтверждён.")
                return redirect("login")
        else:
            register_failed_attempt(ip, email)
            messages.error(request, "Неверные учетные данные.")
            return redirect("login")

    return render(request, "authentication/login.html")


def logout_view(request):
    if request.user.is_authenticated:
        user_email = request.user.email

        user_action_logger.info(f"✅ ВЫХОД: Пользователь {user_email} вышел из системы")

    logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect("login")


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    my_services = Service.objects.filter(author=request.user).select_related("game")

    if request.method == "POST":
        new_username = request.POST.get("username")
        if new_username:
            request.user.username = new_username
            user_action_logger.info(
                f"♻️UPDATE: Пользователь {new_username} обновил имя пользывателя"
            )
        if "avatar" in request.FILES:
            request.user.avatar = request.FILES["avatar"]
            user_action_logger.info(
                f"♻️UPDATE: Пользователь {new_username} обновил аватар"
            )
        request.user.save()
        messages.success(request, "Профиль обновлен")
        return redirect("profile")

    return render(request, "authentication/profile.html", {"my_services": my_services})
