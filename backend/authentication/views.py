"""
Auth views:
- Register
- Verify email
- Login (rate limit)
- Logout
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.cache import cache
from .models import User
from .services.verification_service import create_verification, verify_code
from .services.email_service import send_verification_email

LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_BLOCK_TIME = 300


def is_blocked(ip, email):
    key = f"login_attempts:{ip}:{email}"
    attempts = cache.get(key, 0)
    return attempts >= LOGIN_ATTEMPTS_LIMIT

def home(request):
    return render(request, 'authentication/home.html')



def register_failed_attempt(ip, email):
    key = f"login_attempts:{ip}:{email}"
    attempts = cache.get(key, 0)
    cache.set(key, attempts + 1, timeout=LOGIN_BLOCK_TIME)


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "User already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False
        )

        code = create_verification(user)
        send_verification_email(user, code)

        request.session["verification_user_id"] = user.id
        return redirect("verify_email")

    return render(request, "authentication/register.html")


def verify_email_view(request):
    user_id = request.session.get("verification_user_id")
    if not user_id:
        return redirect("register")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        code = request.POST.get("code")

        if verify_code(user, code):
            user.is_active = True
            user.is_verified = True
            user.save()
            login(request, user)
            return redirect("/")

        messages.error(request, "Invalid or expired code.")

    return render(request, "authentication/verify_email.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        ip = request.META.get("REMOTE_ADDR")

        if is_blocked(ip, email):
            messages.error(request, "Too many attempts. Try later.")
            return redirect("login")

        user = authenticate(request, email=email, password=password)

        if user and user.is_verified:
            cache.delete(f"login_attempts:{ip}:{email}")
            login(request, user)
            request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect("/")

        register_failed_attempt(ip, email)
        messages.error(request, "Invalid credentials.")

    return render(request, "authentication/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")