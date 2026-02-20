from django.db import models


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
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="services/", blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.game.name})"
