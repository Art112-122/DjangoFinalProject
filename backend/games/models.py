from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings


class Game(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField(max_length=500)
    image = models.ImageField(upload_to="games/")

    def __str__(self):
        return self.name


class Service(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="services",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="services/", blank=True, null=True)

    def get_average_rating(self):
        from django.db.models import Avg

        return self.reviews.aggregate(Avg("rating"))["rating__avg"] or 0

    def __str__(self):
        return f"{self.title} ({self.game.name})"



class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.email}"
        return "Анонимная корзина"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.game.name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.game.price * self.quantity
    

class Review(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="От 1 до 5",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["service", "author"], name="unique_review")
        ]

    def __str__(self):
        return f"Отзыв от {self.author} на {self.service}"