"""
Custom User model
Email используется как username
"""
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=False)
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default.png", blank=True
    )
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_seller_rating(self):
        from games.models import Review

        rating = Review.objects.filter(service__author=self).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        return round(rating, 1) if rating else 0

    def get_rating_range(self):
        return range(int(self.get_seller_rating()))

    def get_empty_rating_range(self):
        return range(5 - int(self.get_seller_rating()))

    def __str__(self):
        return f"{self.username} ({self.email})"